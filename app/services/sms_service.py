import logging
from typing import Optional

import httpx

from app.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

_eskiz_token: Optional[str] = None


async def get_token() -> str:
    global _eskiz_token

    if _eskiz_token:
        return _eskiz_token

    if not settings.ESKIZ_EMAIL or not settings.ESKIZ_PASSWORD:
        raise AppError("Eskiz SMS sozlamalari to'ldirilmagan", status_code=500)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{settings.ESKIZ_BASE_URL}/auth/login",
                data={
                    "email": settings.ESKIZ_EMAIL,
                    "password": settings.ESKIZ_PASSWORD,
                },
            )
            response.raise_for_status()
            result = response.json()
            _eskiz_token = result["data"]["token"]
            logger.info("Eskiz token obtained successfully")
            return _eskiz_token
    except httpx.HTTPStatusError as e:
        logger.error(f"Eskiz auth failed: {e.response.status_code} - {e.response.text}")
        raise AppError("Eskiz autentifikatsiya xatosi", status_code=502)
    except Exception as e:
        logger.error(f"Eskiz auth error: {e}")
        raise AppError("SMS xizmatiga ulanishda xatolik", status_code=502)


async def send_sms(phone: str, message: str) -> dict:
    token = await get_token()

    phone = phone.lstrip("+")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{settings.ESKIZ_BASE_URL}/message/sms/send",
                headers={"Authorization": f"Bearer {token}"},
                data={
                    "mobile_phone": phone,
                    "message": message,
                    "from": "4546",
                },
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"SMS sent to {phone}: status={result.get('status')}")
            return result
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            global _eskiz_token
            _eskiz_token = None
            return await send_sms(phone, message)
        logger.error(f"SMS send failed: {e.response.status_code} - {e.response.text}")
        raise AppError("SMS yuborishda xatolik", status_code=502)
    except Exception as e:
        logger.error(f"SMS send error: {e}")
        raise AppError("SMS xizmatiga ulanishda xatolik", status_code=502)


async def send_otp(phone: str, code: str) -> dict:
    message = f"Alif24 tasdiqlash kodi: {code}. Kodni hech kimga bermang."
    return await send_sms(phone, message)
