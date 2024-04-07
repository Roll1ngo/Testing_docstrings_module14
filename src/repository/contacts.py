from datetime import timedelta

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    request = select(Contact).filter_by(user_id=user.id).offset(offset).limit(limit)
    contacts = await db.execute(request)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    request = select(Contact).filter_by(id=contact_id, user_id=user.id)
    contact = await db.execute(request)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
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


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    request = select(Contact).filter_by(id=contact_id, user_id=user.id)
    response = await db.execute(request)
    contact = response.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_birthdays(db: AsyncSession, user: User):
    request = select(Contact).filter(
        Contact.user_id == user.id,
        func.extract('month', Contact.birthday) == func.extract('month', func.current_date() + timedelta(days=7)),
        func.extract('day', Contact.birthday) >= func.extract('day', func.current_date()),
        func.extract('day', Contact.birthday) <= func.extract('day', func.current_date() + timedelta(days=7))
    )

    contacts = await db.execute(request)
    return contacts.scalars().all()


async def search_contacts(search_string, db: AsyncSession, user: User):
    request = select(Contact).filter(Contact.user_id == user.id,
                                     or_(
                                         Contact.name.ilike(f'%{search_string}%'),
                                         Contact.last_name.ilike(f'%{search_string}%'),
                                         Contact.email.ilike(f'%{search_string}%'),
                                         Contact.phone_number.ilike(f'%{search_string}%')
                                     ))
    contacts = await db.execute(request)

    return contacts.scalars().all()
