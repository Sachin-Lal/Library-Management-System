from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    uid: str
    mid: Optional[str] = None
    username: str


class RegistrationRequest(BaseModel):
    fname: str = Field(min_length=1, alias="FName")
    lname: str = Field(min_length=1, alias="LName")
    phone: str = Field(min_length=1)
    email: EmailStr
    address: str = Field(min_length=1)
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)

    model_config = {"populate_by_name": True}


class RegistrationDecision(BaseModel):
    payment_recorded: bool = True


class MemberCreate(BaseModel):
    fname: str = Field(min_length=1)
    lname: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    email: EmailStr
    address: str = Field(min_length=1)
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)


class MemberUpdate(BaseModel):
    fname: Optional[str] = Field(default=None, min_length=1)
    lname: Optional[str] = Field(default=None, min_length=1)
    phone: Optional[str] = Field(default=None, min_length=1)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(default=None, min_length=1)


class MemberStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        if value not in {"Active", "Inactive"}:
            raise ValueError("status must be Active or Inactive")
        return value


class BookCreate(BaseModel):
    name: str = Field(min_length=1)
    author: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    total_copies: int = Field(gt=0)


class BookUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    author: Optional[str] = Field(default=None, min_length=1)
    publisher: Optional[str] = Field(default=None, min_length=1)
    total_copies: Optional[int] = Field(default=None, gt=0)


class BorrowRequestCreate(BaseModel):
    bid: str = Field(min_length=1)


class ReturnRequest(BaseModel):
    return_date: date = Field(default_factory=date.today)
