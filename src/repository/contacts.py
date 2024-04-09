from datetime import timedelta
from typing import Sequence

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User) -> Sequence[Contact]:
    """
    Asynchronous function to retrieve a sequence of contacts based on the specified limit, offset, database session, and user.
    Returns a sequence of Contact objects.
    """
    request = select(Contact).filter_by(user_id=user.id).offset(offset).limit(limit)
    contacts = await db.execute(request)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User) -> Contact | None:
    """
    A function to retrieve a contact by its ID using the provided database session and user object.

    Parameters:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The asynchronous database session to execute the query.
        user (User): The user object associated with the contact.

    Returns:
        Contact | None: The retrieved contact object if found, otherwise None.
    """
    request = select(Contact).filter_by(id=contact_id, user_id=user.id)
    contact = await db.execute(request)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User) -> Contact:
    """
    Asynchronously creates a contact using the provided contact data and database session.

    Args:
        body (ContactSchema): The contact data to be used for creating the contact.
        db (AsyncSession): The database session.
        user (User): The user creating the contact.

    Returns:
        Contact: The newly created contact.
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
    """
      Update a contact in the database with the provided contact_id using the information in the body.

      Args:
          contact_id (int): The id of the contact to update.
          body (ContactSchema): The new information to update the contact with.
          db (AsyncSession): The async database session.
          user (User): The user performing the update.

      Returns:
          Contact: The updated contact object.
      """
    request = select(Contact).filter_by(id=contact_id, user_id=user.id)
    response = await db.execute(request)
    contact = response.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User) -> Contact:
    """
    A function that deletes a contact from the database based on the contact id and user id.

    Parameters:
        contact_id (int): The id of the contact to be deleted.
        db (AsyncSession): The database session to execute the deletion operation.
        user (User): The user object associated with the contact.

    Returns:
        Contact: The deleted contact object, if found and deleted successfully.
    """
    request = select(Contact).filter_by(id=contact_id, user_id=user.id)
    response = await db.execute(request)
    contact = response.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_birthdays(db: AsyncSession, user: User) -> Sequence[Contact]:
    """
    A function that retrieves birthdays for a given user that are happening within the next week.

    Parameters:
    - db: An asynchronous database session.
    - user: An instance of the User class.

    Returns:
    - A sequence of Contact objects representing birthdays.
    """
    request = select(Contact).filter(
        Contact.user_id == user.id,
        func.extract('month', Contact.birthday) == func.extract('month', func.current_date() + timedelta(days=7)),
        func.extract('day', Contact.birthday) >= func.extract('day', func.current_date()),
        func.extract('day', Contact.birthday) <= func.extract('day', func.current_date() + timedelta(days=7))
    )

    contacts = await db.execute(request)
    return contacts.scalars().all()


async def search_contacts(search_string, db: AsyncSession, user: User) -> Sequence[Contact]:
    """
    A function that searches for contacts based on a search string for a specific user in the database.

    Parameters:
        search_string (str): The string to search for in the contacts' name, last name, email, or phone number.
        db (AsyncSession): The asynchronous database session to execute the search query.
        user (User): The user object to filter the contacts by.

    Returns:
        Sequence[Contact]: A sequence of Contact objects that match the search criteria.
    """
    request = select(Contact).filter(Contact.user_id == user.id,
                                     or_(
                                         Contact.name.ilike(f'%{search_string}%'),
                                         Contact.last_name.ilike(f'%{search_string}%'),
                                         Contact.email.ilike(f'%{search_string}%'),
                                         Contact.phone_number.ilike(f'%{search_string}%')
                                     ))
    contacts = await db.execute(request)

    return contacts.scalars().all()
