import uuid

from sqlalchemy import String, Date, DateTime, func, ForeignKey, Boolean
from datetime import date
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Contact(Base):
    """
       This class represents a contact in the database.

       Attributes:
       id (int): The unique identifier for the contact.
       name (str): The name of the contact.
       last_name (str): The last name of the contact.
       email (str): The email address of the contact.
       phone_number (str): The phone number of the contact.
       birthday (date): The birthday of the contact.
       user_id (UUID): The unique identifier for the user associated with the contact.
       user (User): The user associated with the contact.

       Methods:
       None
       """
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id',
                                                                         ondelete='CASCADE'), nullable=True,)
    user: Mapped['User'] = relationship('User', backref='contacts',
                                        lazy='joined', cascade='all, delete')


class User(Base):
    """
      This class represents a user in the database.

      Attributes:
      id (UUID): The unique identifier for the user.
      username (str): The username of the user.
      email (str): The email address of the user.
      password (str): The hashed password of the user.
      avatar (str): The avatar of the user.
      refresh_token (str): The refresh token of the user.
      email_verified (bool): Whether the user's email has been verified.
      open_verification_letter (bool): Whether the user has opened the verification letter.
      created_at (date): The date and time when the user was created.
      updated_at (date): The date and time when the user was last updated.

      Methods:
      None
      """
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    open_verification_letter: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
