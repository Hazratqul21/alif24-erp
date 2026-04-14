from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.utils.validators import validate_subdomain, validate_email, validate_phone


class PlanInfo(BaseModel):
    id: int
    name: str
    max_users: int = 100
    max_students: int = 500
    max_teachers: int = 50

    model_config = {"from_attributes": True}


class TenantCreate(BaseModel):
    subdomain: str
    name: str
    logo: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    plan_id: Optional[int] = None

    @field_validator("subdomain")
    @classmethod
    def check_subdomain(cls, v: str) -> str:
        if not validate_subdomain(v):
            raise ValueError(
                "Subdomen noto'g'ri. Faqat kichik harflar, raqamlar va chiziqcha (-) ishlatilishi mumkin"
            )
        return v

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


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    logo: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    subscription_end: Optional[date] = None
    plan_id: Optional[int] = None
    max_users: Optional[int] = None
    max_students: Optional[int] = None

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


class TenantResponse(BaseModel):
    id: int
    subdomain: str
    name: str
    logo: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    subscription_end: Optional[date] = None
    max_users: int = 100
    max_students: int = 500
    plan: Optional[PlanInfo] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TenantListResponse(BaseModel):
    items: list[TenantResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
