import pickle

import redis
from fastapi import Depends, HTTPException, status

from src.conf.config import config
from src.entity.models import User
from src.database.connect import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import users as repository_users

cache = redis.Redis(host=config.REDIS_DOMAIN,
                    port=config.REDIS_PORT,
                    db=0,
                    password=config.REDIS_PASSWORD, )

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_user_cache(email: str, db: AsyncSession = Depends(get_db)) -> User:
    user_hash = str(email)
    user = cache.get(user_hash)
    if user is None:
        print("User from database")
        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        cache.set(user_hash, pickle.dumps(user))
        cache.expire(user_hash, 300)
    else:
        print("User from cache")
        user = pickle.loads(user)
    return user


async def update_user_cache(user: User, time=300) -> None:
    cache.set(user.email, pickle.dumps(user))
    cache.expire(user.email, time)
