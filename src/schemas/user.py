from pydantic import BaseModel, Field, EmailStr, ConfigDict
from uuid import UUID


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=1000)
    email: EmailStr
    password: str = Field(min_length=3, max_length=250)

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    avatar: str | None
    email_verified: bool | None

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RequestEmail(BaseModel):
    email: EmailStr
