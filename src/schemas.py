from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class ContactsModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    born_date: date


class ContactsResponse(ContactsModel):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ContactsStatusUpdate(BaseModel):
    done: bool

class ContactsUpdate(BaseModel):
    done: bool


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str 
    password: str = Field(min_length=6, max_length=30)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr