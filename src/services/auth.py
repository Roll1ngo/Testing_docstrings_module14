from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.connect import get_db
from src.entity.models import User
from src.conf.config import config
from src.services.cache_redis import get_user_cache


class Auth:
    """
    A class for handling authentication-related tasks.

    Attributes:
        pwd_context (CryptContext): A context for password hashing and verification.
        SECRET_KEY (str): The secret key for JWT signing.
        ALGORITHM (str): The algorithm for JWT signing.

    Methods:
        verify_password(plain_password, hashed_password): Verify a plain password against a hashed password.
        get_password_hash(password): Hash a password.
        create_access_token(data, expires_delta): Create a new access token.
        create_refresh_token(data, expires_delta): Create a new refresh token.
        decode_refresh_token(refresh_token): Decode a refresh token.
        get_current_user(token, db): Get the current user from a token.
        create_email_token(data): Create a new email token.
        get_email_from_token(token): Get the email from an email token.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY
    ALGORITHM = config.ALGORITHM

    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        Verify a plain password against a hashed password.

        Parameters:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
          Generate the password hash for the given password.
          Parameters:
              password (str): The password to generate the hash for.
          Returns:
              str: The hashed password.
          """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="rest_api/auth/login")

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Generate an access token based on the provided data and expiration time.

        Parameters:
            data (dict): The data to be encoded into the access token.
            expires_delta (Optional[float]): The expiration time for the access token in seconds.
            Defaults to 15 minutes if not provided.

        Returns:
            str: The encoded access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Generate a refresh token using the provided data and expiration delta.

        Parameters:
            data (dict): The data to be encoded into the refresh token.
            expires_delta (Optional[float]): The expiration time delta in seconds (default is 7 days).

        Returns:
            str: The encoded refresh token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decode a refresh token and return the email.

        Parameters:
            refresh_token (str): The refresh token to decode.

        Returns:
            str: The email associated with the refresh token.

        Raises:
            HTTPException: If the token has an invalid scope or could not be validated.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme),
                               db: AsyncSession = Depends(get_db)) -> User:
        """
        Get the current user from a token.

        Parameters:
            token (str, optional): The token to decode.
            db (AsyncSession, optional): The database session.

        Returns:
            User: The current user.

        Raises:
            HTTPException: If the token has an invalid scope or could not be validated.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user: User = await get_user_cache(email, db)
        return user

    def create_email_token(self, data: dict) -> str:
        """
        Create a new email token.

        Parameters:
            data (dict): The data to encode in the token.

        Returns:
            str: The encoded email token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str) -> str:
        """
             Get the email from the provided token.
             Parameters:
                 token (str): The token from which to extract the email.
             Returns:
                 str: The email extracted from the token.
             """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()  # Create an instance of the Auth class.
