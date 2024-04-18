import pickle

from redis import Redis
from fastapi import Depends, HTTPException, status

from src.conf.config import config
from src.entity.models import User
from src.database.connect import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import users as repository_users

# Create a Redis cache instance.
cache = Redis(host=config.REDIS_DOMAIN,
              port=config.REDIS_PORT,
              db=0,
              password=config.REDIS_PASSWORD, )

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_user_cache(email: str, db: AsyncSession = Depends(get_db)) -> User:
    """
    Retrieve a user from cache if available, otherwise fetch from the database.

    Parameters:
        email (str): The email of the user to retrieve.
        db (AsyncSession): The asynchronous database session

    Returns:
        User: The user object retrieved either from the cache or the database.
    """
    user_hash = str(email)
    user = cache.get(user_hash)
    if user is None:
        user = await repository_users.get_user_by_email(email, db)
        # cache.set(user_hash, pickle.dumps(user))
        # cache.expire(user_hash, 1)
    else:
        user = pickle.loads(user)
    return user


async def update_user_cache(user: User, time=300) -> None:
    """
    Update the user cache with the provided user object and set an expiration time.

    Parameters:
        user (User): The user object to be cached.
        time (int): The expiration time for the cache in seconds. Defaults to 300 seconds.

    Returns:
        None
    """
    cache.set(user.email, pickle.dumps(user))
    cache.expire(user.email, time)
