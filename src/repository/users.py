from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.connect import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """
    A function to retrieve a user from the database based on their email address.

    Parameters:
    - email: a string representing the user's email address
    - db: an AsyncSession dependency representing the database session

    Returns:
    - User: the user object corresponding to the provided email address, if found
    """
    request = select(User).filter_by(email=email)
    user = await db.execute(request)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession) -> User:
    """
    Asynchronously creates a new user using the provided UserSchema object and adds it to the database session.
    If the user has a Gravatar associated with the provided email, it retrieves and sets the avatar for the user.
    Parameters:
        body (UserSchema): The UserSchema object containing user information.
        db (AsyncSession, optional): The AsyncSession database session (default: Depends(get_db)).
    Returns:
        User: The newly created User object.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def email_verified(email: str, db: AsyncSession) -> None:
    """
    An asynchronous function that marks a user's email as verified in the database.

    Args:
        email (str): The email address of the user to be verified.
        db (AsyncSession): The asynchronous database session.

    Returns:
        None
    """
    user = await get_user_by_email(email, db)
    user.email_verified = True
    await db.commit()


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    Update the refresh token for a user in the database.

    Args:
        user (User): The user object to update the token for.
        token (str): The new token to set for the user.
        db (AsyncSession): The async database session to commit the changes to.

    Returns:
        None
    """
    user.refresh_token = token
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    Update the avatar URL for a user in the database.

    Args:
        email (str): The email of the user.
        url (str | None): The new avatar URL to update. Can be None.
        db (AsyncSession): The async database session.

    Returns:
        User: The updated user object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
