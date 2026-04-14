import re
from datetime import date


PHONE_REGEX = re.compile(r"^\+998\d{9}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
SUBDOMAIN_REGEX = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_DOC_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def validate_phone(phone: str) -> bool:
    return bool(PHONE_REGEX.match(phone))


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def validate_subdomain(subdomain: str) -> bool:
    if not SUBDOMAIN_REGEX.match(subdomain):
        return False
    reserved = {"www", "admin", "api", "mail", "ftp", "test", "dev", "staging"}
    return subdomain not in reserved


def validate_birth_date(birth_date: date) -> bool:
    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    return 3 <= age <= 100
