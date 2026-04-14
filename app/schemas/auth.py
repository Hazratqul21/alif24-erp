from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.utils.validators import validate_phone


class LoginRequest(BaseModel):
    email_or_phone: str
    password: str


class UserInfo(BaseModel):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: str
    last_name: str
    roles: list[str] = []

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserInfo


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Parol kamida 8 ta belgidan iborat bo'lishi kerak")
        if not any(c.isdigit() for c in v):
            raise ValueError("Parolda kamida 1 ta raqam bo'lishi kerak")
        if not any(c.isupper() for c in v):
            raise ValueError("Parolda kamida 1 ta katta harf bo'lishi kerak")
        return v


class ForgotPasswordRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str) -> str:
        if not validate_phone(v):
            raise ValueError("Telefon raqam formati noto'g'ri. Namuna: +998901234567")
        return v


class ResetPasswordRequest(BaseModel):
    phone: str
    code: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Parol kamida 8 ta belgidan iborat bo'lishi kerak")
        return v

    @field_validator("code")
    @classmethod
    def code_format(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Tasdiqlash kodi 6 ta raqamdan iborat bo'lishi kerak")
        return v


class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_uri: str


class TwoFactorVerifyRequest(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def code_format(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Tasdiqlash kodi 6 ta raqamdan iborat bo'lishi kerak")
        return v


class UserProfile(BaseModel):
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True
    totp_enabled: bool = False
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    roles: list[str] = []

    model_config = {"from_attributes": True}
