from typing import Any

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession


from src.database.connect import get_db
from src.entity.models import User
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email
from src.services.cache_redis import get_user_cache, update_user_cache

router = APIRouter(prefix='/auth', tags=['auth'])  # Creates a new router for authentication-related routes.
get_refresh_token = HTTPBearer()  # Sets up a function to validate JWT tokens in incoming requests.

templates = Jinja2Templates(directory='templates')  # Initializes a Jinja2 template engine for rendering HTML templates.


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, background_task: BackgroundTasks, request: Request,
                 db: AsyncSession = Depends(get_db)) -> User:
    """
    Asynchronous function for user signup.
    Parameters:
    - body: UserSchema object representing the user information
    - background_task: BackgroundTasks object for handling background tasks
    - request: Request object representing the incoming request
    - db: AsyncSession object for database interaction
    Returns:
    - UserResponse object representing the newly created user
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    await update_user_cache(new_user)
    background_task.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> dict:
    """
    Asynchronous function for user login.
    Parameters:
    - body: OAuth2PasswordRequestForm object representing the user credentials
    - db: AsyncSession object for database interaction
    Returns:
    - Dictionary containing the access token and refresh token
    """
    user = await get_user_cache(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(input_refresh: str = None,
                        credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)) -> dict:
    """
    Asynchronous function for refreshing the user's access token.
    Parameters:
    - input_refresh: str representing the refresh token
    - credentials: HTTPAuthorizationCredentials object representing the user's credentials
    - db: AsyncSession object for database interaction
    - user: User object representing the current user
    Returns:
    - Dictionary containing the new access token and refresh token
    """
    token = input_refresh if input_refresh else credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await get_user_cache(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}', response_class=HTMLResponse)
async def confirmed_email(token: str, request: Request, db: AsyncSession = Depends(get_db)) -> Any | dict:
    """
    Asynchronous function for confirming the user's email address.
    Parameters:
    - token: str representing the token used for email verification
    - request: Request object representing the incoming request
    - db: AsyncSession object for database interaction
    Returns:
    - HTMLResponse object containing the email verification response
    """
    email = await auth_service.get_email_from_token(token)
    user = await get_user_cache(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.email_verified:
        return {"message": "Your email is already confirmed"}
    await repositories_users.email_verified(email, db)
    return templates.TemplateResponse('response_email_verification.html', context={'request': request})


@router.post('/resent_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)) -> dict:
    """
    Asynchronous function for resending the email verification email.
    Parameters:
    - body: RequestEmail object representing the user's email address
    - background_tasks: BackgroundTasks object for handling background tasks
    - request: Request object representing the incoming request
    - db: AsyncSession object for database interaction
    Returns:
    - Dictionary containing a message indicating that the email has been sent
    """
    user = await get_user_cache(body.email, db)

    if user.email_verified:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.get('/check/{email}')
async def check_opening_email(email: str, db: AsyncSession = Depends(get_db)) -> FileResponse:
    """
    A function that checks and records to database the opening of a verification email for a user.

    Parameters:
    - email: a string representing the email address of the user
    - db: an AsyncSession dependency used to interact with the database

    Returns:
    - FileResponse: a response containing an image file for the verification
    """
    user = await get_user_cache(email, db)
    user.open_verification_letter = True
    await db.commit()
    print(f'Opening verification {email} recorded to DB')

    return FileResponse("src/static/loudmouth.png", media_type="image/png", content_disposition_type="inline")
