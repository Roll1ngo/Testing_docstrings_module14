import pickle

import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect import get_db
from src.entity.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.services.cache_redis import update_user_cache
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])


cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET_KEY,
    secure=True,
)


@router.get("/me", response_model=UserResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=20))], )
async def get_current_user(user: User = Depends(auth_service.get_current_user)) -> User:
    """
    A function to get the current user, taking in a user object as a parameter and returning a user object.
    """
    return user


#
@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))], )
async def get_current_user(
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
) -> User:
    """
    Asynchronous function to update the current user's avatar.

    Args:
        file (UploadFile): The file containing the new avatar image.
        user (User): The current user.
        db (AsyncSession): The asynchronous session for database operations.

    Returns:
        User: The updated user object after avatar url has been updated.
    """
    public_id = f"FastAPI_contacts/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    print(f"res: {res}")
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    print(f"res_url: {res_url}")
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    await update_user_cache(user)
    return user
