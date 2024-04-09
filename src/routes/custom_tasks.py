from typing import List, Sequence

from fastapi import Depends, APIRouter
from sqlalchemy import select


from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.database.connect import get_db
from src.schemas.user import UserResponse

router = APIRouter(prefix='/custom_tasks', tags=['dev_temporary'])


@router.get("/get_users", response_model=List[UserResponse])
async def get_signup_users(db: AsyncSession = Depends(get_db)) -> Sequence[User]:
    """
    Asynchronous function for retrieving a list of users.
    Parameters:
    - db: AsyncSession object for database interaction
    Returns:
    - Sequence of User objects representing the list of users
    """
    request = select(User)
    response = await db.execute(request)
    result = response.scalars().all()
    return result


