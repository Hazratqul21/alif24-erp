from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.dependencies import get_db, get_current_user
from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_totp_secret,
    get_totp_uri,
    verify_totp,
    generate_otp_code,
)
from app.core.cache import get_redis
from app.core.exceptions import (
    UnauthorizedError,
    NotFoundError,
    ValidationError,
    ConflictError,
)
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserInfo,
    RefreshRequest,
    RefreshResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    UserProfile,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

OTP_TTL_SECONDS = 300


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    identifier = body.email_or_phone.strip()

    result = await db.execute(
        text("""
            SELECT id, email, phone, first_name, last_name,
                   password_hash, is_active, totp_enabled, totp_secret, deleted_at
            FROM users
            WHERE (email = :ident OR phone = :ident)
            LIMIT 1
        """),
        {"ident": identifier},
    )
    user = result.fetchone()

    if not user:
        raise UnauthorizedError("Email yoki telefon raqam noto'g'ri")

    if user[9] is not None:
        raise UnauthorizedError("Bu hisob o'chirilgan")

    if not user[6]:
        raise UnauthorizedError("Hisob faol emas. Administrator bilan bog'laning")

    if not verify_password(body.password, user[5]):
        raise UnauthorizedError("Parol noto'g'ri")

    user_id = str(user[0])

    roles_result = await db.execute(
        text("""
            SELECT r.name FROM roles r
            JOIN user_roles ur ON ur.role_id = r.id
            WHERE ur.user_id = :uid
        """),
        {"uid": user_id},
    )
    roles = [row[0] for row in roles_result]

    token_data = {
        "sub": user_id,
        "email": user[1],
        "phone": user[2],
        "roles": roles,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    await db.execute(
        text("""
            UPDATE users
            SET refresh_token = :rt, last_login = :now
            WHERE id = :uid
        """),
        {"rt": refresh_token, "now": datetime.now(timezone.utc), "uid": user_id},
    )
    await db.commit()

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.APP_ENV != "development",
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserInfo(
            id=user_id,
            email=user[1],
            phone=user[2],
            first_name=user[3],
            last_name=user[4],
            roles=roles,
        ),
    )


@router.post("/logout")
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    await db.execute(
        text("UPDATE users SET refresh_token = NULL WHERE id = :uid"),
        {"uid": current_user["id"]},
    )
    await db.commit()

    response.delete_cookie("access_token")
    return {"detail": "Tizimdan muvaffaqiyatli chiqdingiz"}


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    body: RefreshRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_refresh_token(body.refresh_token)
    if payload is None:
        raise UnauthorizedError("Refresh token yaroqsiz yoki muddati tugagan")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Token ma'lumotlari noto'g'ri")

    result = await db.execute(
        text("""
            SELECT id, email, phone, is_active, refresh_token, deleted_at
            FROM users WHERE id = :uid
        """),
        {"uid": user_id},
    )
    user = result.fetchone()

    if not user or user[5] is not None:
        raise UnauthorizedError("Foydalanuvchi topilmadi")

    if not user[3]:
        raise UnauthorizedError("Hisob faol emas")

    if user[4] != body.refresh_token:
        raise UnauthorizedError("Refresh token mos kelmadi")

    roles_result = await db.execute(
        text("""
            SELECT r.name FROM roles r
            JOIN user_roles ur ON ur.role_id = r.id
            WHERE ur.user_id = :uid
        """),
        {"uid": user_id},
    )
    roles = [row[0] for row in roles_result]

    token_data = {
        "sub": str(user[0]),
        "email": user[1],
        "phone": user[2],
        "roles": roles,
    }
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)

    await db.execute(
        text("UPDATE users SET refresh_token = :rt WHERE id = :uid"),
        {"rt": new_refresh, "uid": user_id},
    )
    await db.commit()

    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=settings.APP_ENV != "development",
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return RefreshResponse(access_token=new_access, refresh_token=new_refresh)


@router.get("/me", response_model=UserProfile)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        text("""
            SELECT id, email, phone, first_name, last_name, middle_name,
                   birth_date, gender, avatar, is_active, totp_enabled,
                   last_login, created_at
            FROM users WHERE id = :uid
        """),
        {"uid": current_user["id"]},
    )
    user = result.fetchone()
    if not user:
        raise NotFoundError("Foydalanuvchi")

    return UserProfile(
        id=str(user[0]),
        email=user[1],
        phone=user[2],
        first_name=user[3],
        last_name=user[4],
        middle_name=user[5],
        birth_date=str(user[6]) if user[6] else None,
        gender=user[7],
        avatar=user[8],
        is_active=user[9],
        totp_enabled=user[10],
        last_login=user[11],
        created_at=user[12],
        roles=current_user.get("roles", []),
    )


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        text("SELECT password_hash FROM users WHERE id = :uid"),
        {"uid": current_user["id"]},
    )
    row = result.fetchone()
    if not row:
        raise NotFoundError("Foydalanuvchi")

    if not verify_password(body.old_password, row[0]):
        raise ValidationError("Joriy parol noto'g'ri")

    new_hash = hash_password(body.new_password)
    await db.execute(
        text("UPDATE users SET password_hash = :ph, updated_at = NOW() WHERE id = :uid"),
        {"ph": new_hash, "uid": current_user["id"]},
    )
    await db.commit()

    return {"detail": "Parol muvaffaqiyatli o'zgartirildi"}


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("SELECT id FROM users WHERE phone = :phone AND deleted_at IS NULL"),
        {"phone": body.phone},
    )
    user = result.fetchone()
    if not user:
        raise NotFoundError("Bu telefon raqam bilan foydalanuvchi")

    otp = generate_otp_code()

    redis = await get_redis()
    await redis.set(f"otp:reset:{body.phone}", otp, ex=OTP_TTL_SECONDS)

    # TODO: Eskiz SMS orqali OTP yuborish

    return {"detail": "Tasdiqlash kodi yuborildi"}


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    redis = await get_redis()
    stored_otp = await redis.get(f"otp:reset:{body.phone}")

    if not stored_otp:
        raise ValidationError("Tasdiqlash kodi topilmadi yoki muddati tugagan")

    if stored_otp != body.code:
        raise ValidationError("Tasdiqlash kodi noto'g'ri")

    result = await db.execute(
        text("SELECT id FROM users WHERE phone = :phone AND deleted_at IS NULL"),
        {"phone": body.phone},
    )
    user = result.fetchone()
    if not user:
        raise NotFoundError("Foydalanuvchi")

    new_hash = hash_password(body.new_password)
    await db.execute(
        text("""
            UPDATE users
            SET password_hash = :ph, refresh_token = NULL, updated_at = NOW()
            WHERE id = :uid
        """),
        {"ph": new_hash, "uid": user[0]},
    )
    await db.commit()

    await redis.delete(f"otp:reset:{body.phone}")

    return {"detail": "Parol muvaffaqiyatli yangilandi"}


@router.post("/2fa/enable", response_model=TwoFactorSetupResponse)
async def enable_2fa(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        text("SELECT totp_enabled, email FROM users WHERE id = :uid"),
        {"uid": current_user["id"]},
    )
    row = result.fetchone()
    if not row:
        raise NotFoundError("Foydalanuvchi")

    if row[0]:
        raise ConflictError("Ikki bosqichli tasdiqlash allaqachon yoqilgan")

    secret = generate_totp_secret()
    email = row[1] or current_user.get("phone", "user")
    qr_uri = get_totp_uri(secret, email)

    await db.execute(
        text("UPDATE users SET totp_secret = :secret WHERE id = :uid"),
        {"secret": secret, "uid": current_user["id"]},
    )
    await db.commit()

    return TwoFactorSetupResponse(secret=secret, qr_uri=qr_uri)


@router.post("/2fa/verify")
async def verify_2fa(
    body: TwoFactorVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        text("SELECT totp_secret, totp_enabled FROM users WHERE id = :uid"),
        {"uid": current_user["id"]},
    )
    row = result.fetchone()
    if not row or not row[0]:
        raise ValidationError("Avval 2FA ni yoqing")

    if not verify_totp(row[0], body.code):
        raise ValidationError("Tasdiqlash kodi noto'g'ri")

    if not row[1]:
        await db.execute(
            text("UPDATE users SET totp_enabled = true WHERE id = :uid"),
            {"uid": current_user["id"]},
        )
        await db.commit()

    return {"detail": "Ikki bosqichli tasdiqlash muvaffaqiyatli yoqildi"}


@router.post("/2fa/disable")
async def disable_2fa(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        text("SELECT totp_enabled FROM users WHERE id = :uid"),
        {"uid": current_user["id"]},
    )
    row = result.fetchone()
    if not row or not row[0]:
        raise ValidationError("Ikki bosqichli tasdiqlash yoqilmagan")

    await db.execute(
        text("UPDATE users SET totp_secret = NULL, totp_enabled = false WHERE id = :uid"),
        {"uid": current_user["id"]},
    )
    await db.commit()

    return {"detail": "Ikki bosqichli tasdiqlash o'chirildi"}
