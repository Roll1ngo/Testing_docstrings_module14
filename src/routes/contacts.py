from typing import Sequence

from fastapi import APIRouter, HTTPException, status, Depends, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactResponse
from src.entity.models import User, Contact
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])  # Creates a new router for contacts-related routes


@router.get('/', response_model=list[ContactResponse],
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contacts(limit: int = Query(10, ge=10, le=500),
                       offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)) -> Sequence[Contact]:
    """
    Get a list of contacts.

    Parameters:
        limit (int, optional): The maximum number of contacts to return. Default is 10.
        offset (int, optional): The number of contacts to skip before starting to collect the result set. Default is 0.
        db (AsyncSession, optional): The database session. Provided by the dependency `get_db`.
        user (User, optional): The current user. Provided by the dependency `auth_service.get_current_user`.

    Returns:
        Sequence[Contact]: A list of contacts.

    Raises:
        HTTPException: If the request is rate limited.
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_contact(contact_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    Asynchronous function to get a contact by ID.
    Parameters:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The asynchronous database session.
        user (User): The current user.
    Returns:
        Contact: The retrieved contact.
    Raises:
        HTTPException: If the contact is not found, raises HTTP 404 Not Found error.
    """
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def create_contact(body: ContactSchema,
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    Create a new contact.

    Parameters:
        body (ContactSchema): The data for the new contact.
        db (AsyncSession, optional): The database session. Provided by the dependency `get_db`.
        user (User, optional): The current user. Provided by the dependency `auth_service.get_current_user`.

    Returns:
        Contact: The created contact.

    Raises:
        HTTPException: If the request is rate limited.
    """
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}', status_code=status.HTTP_201_CREATED,
            response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_contact(body: ContactSchema, contact_id: int = Path(qe=1),
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    Update an existing contact.

    Parameters:
        body (ContactSchema): The data for the updated contact.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession, optional): The database session. Provided by the dependency `get_db`.
        user (User, optional): The current user. Provided by the dependency `auth_service.get_current_user`.

    Returns:
        Contact: The updated contact.

    Raises:
        HTTPException: If the request is rate limited or the contact is not found.
    """
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete('/{contact_id}', dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def delete_contact(contact_id: int = Path(qe=1),
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user),
                         ) -> str:
    """
    Delete a contact.

    Parameters:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession, optional): The database session. Provided by the dependency `get_db`.
        user (User, optional): The current user. Provided by the dependency `auth_service.get_current_user`.

    Returns:
        str: A message indicating that the contact has been deleted.

    Raises:
        HTTPException: If the request is rate limited or the contact is not found.
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return f"{contact.name} {contact.last_name} has been deleted"


@router.get('/birthdate/', response_model=list[ContactResponse],
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_birthdays(db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)) -> Sequence[Contact]:
    """
    Get a list of contacts with upcoming seven birthdays.

    Parameters:
        db (AsyncSession, optional): The database session. Provided by the dependency `get_db`.
        user (User, optional): The current user. Provided by the dependency `auth_service.get_current_user`.

    Returns:
        Sequence[Contact]: A list of contacts with upcoming birthdays.

    Raises:
        HTTPException: If the request is rate limited.
    """
    contacts = await repositories_contacts.get_birthdays(db, user)
    return contacts


@router.get('/search/{search_string}', response_model=list[ContactResponse],
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def search_contacts(search_string: str = Path(min_length=2, max_length=20),
                          db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)) -> Sequence[Contact]:
    """
    Search for contacts.

    Parameters:
        search_string (str): The search string to use for the search.
        db (AsyncSession, optional): The database session. Provided by the dependency `get_db`.
        user (User, optional): The current user. Provided by the dependency `auth_service.get_current_user`.

    Returns:
        Sequence[Contact]: A list of contacts that match the search string.

    Raises:
        HTTPException: If the request is rate limited.
    """
    contacts = await repositories_contacts.search_contacts(search_string, db, user)
    return contacts

