from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.utils.validators import validate_phone, validate_email


class UserCreate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    role_ids: list[int] = []

    @field_validator("email")
    @classmethod
    def check_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not validate_email(v):
            raise ValueError("Email formati noto'g'ri")
        return v

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not validate_phone(v):
            raise ValueError("Telefon raqam formati noto'g'ri. Namuna: +998901234567")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Parol kamida 8 ta belgidan iborat bo'lishi kerak")
        return v

    @field_validator("gender")
    @classmethod
    def check_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("male", "female"):
            raise ValueError("Jins faqat 'male' yoki 'female' bo'lishi mumkin")
        return v


class UserUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[list[int]] = None

    @field_validator("email")
    @classmethod
    def check_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not validate_email(v):
            raise ValueError("Email formati noto'g'ri")
        return v

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not validate_phone(v):
            raise ValueError("Telefon raqam formati noto'g'ri. Namuna: +998901234567")
        return v

    @field_validator("gender")
    @classmethod
    def check_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("male", "female"):
            raise ValueError("Jins faqat 'male' yoki 'female' bo'lishi mumkin")
        return v


class RoleInfo(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True
    roles: list[str] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
