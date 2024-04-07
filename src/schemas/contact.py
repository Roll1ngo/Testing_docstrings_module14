from datetime import date


from pydantic import BaseModel, Field, EmailStr


class ContactSchema(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    last_name: str = Field(min_length=3, max_length=100)
    email: EmailStr = Field(min_length=3, max_length=30, description="Input correct email address")
    phone_number: str = Field(min_length=7, max_length=20)
    birthday: date


class ContactResponse(ContactSchema):
    id: int = 1

    class Config:
        from_attributes = True


class BirthdaysResponse(BaseModel):

    birthday: date

    class Config:
        from_attributes = True
