import hashlib
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

from app.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


class BaseGateway(ABC):
    @abstractmethod
    async def create_transaction(self, params: dict) -> dict:
        ...

    @abstractmethod
    async def check_transaction(self, params: dict) -> dict:
        ...


class PaymeGateway(BaseGateway):
    """Payme payment gateway integration."""

    def __init__(self):
        self.merchant_id = settings.PAYME_MERCHANT_ID
        self.secret_key = settings.PAYME_SECRET_KEY

    def _verify_auth(self, auth_header: Optional[str]) -> bool:
        if not auth_header or not self.secret_key:
            return False
        import base64

        expected = base64.b64encode(
            f"Paycom:{self.secret_key}".encode()
        ).decode()
        return auth_header == f"Basic {expected}"

    async def create_transaction(self, params: dict) -> dict:
        try:
            transaction_id = params.get("id")
            amount = params.get("amount", 0)
            account = params.get("account", {})
            invoice_id = account.get("invoice_id")

            logger.info(
                f"Payme CreateTransaction: id={transaction_id}, "
                f"amount={amount}, invoice={invoice_id}"
            )

            return {
                "result": {
                    "create_time": int(time.time() * 1000),
                    "transaction": transaction_id,
                    "state": 1,
                }
            }
        except Exception as e:
            logger.error(f"Payme CreateTransaction error: {e}")
            raise AppError("Payme tranzaksiya xatosi", status_code=500)

    async def check_transaction(self, params: dict) -> dict:
        try:
            transaction_id = params.get("id")

            logger.info(f"Payme CheckTransaction: id={transaction_id}")

            return {
                "result": {
                    "create_time": int(time.time() * 1000),
                    "perform_time": 0,
                    "cancel_time": 0,
                    "transaction": transaction_id,
                    "state": 1,
                    "reason": None,
                }
            }
        except Exception as e:
            logger.error(f"Payme CheckTransaction error: {e}")
            raise AppError("Payme tekshiruv xatosi", status_code=500)

    async def perform_transaction(self, params: dict) -> dict:
        try:
            transaction_id = params.get("id")

            logger.info(f"Payme PerformTransaction: id={transaction_id}")

            return {
                "result": {
                    "transaction": transaction_id,
                    "perform_time": int(time.time() * 1000),
                    "state": 2,
                }
            }
        except Exception as e:
            logger.error(f"Payme PerformTransaction error: {e}")
            raise AppError("Payme bajarish xatosi", status_code=500)

    async def cancel_transaction(self, params: dict) -> dict:
        try:
            transaction_id = params.get("id")
            reason = params.get("reason")

            logger.info(
                f"Payme CancelTransaction: id={transaction_id}, reason={reason}"
            )

            return {
                "result": {
                    "transaction": transaction_id,
                    "cancel_time": int(time.time() * 1000),
                    "state": -1,
                }
            }
        except Exception as e:
            logger.error(f"Payme CancelTransaction error: {e}")
            raise AppError("Payme bekor qilish xatosi", status_code=500)


class ClickGateway(BaseGateway):
    """Click payment gateway integration."""

    def __init__(self):
        self.merchant_id = settings.CLICK_MERCHANT_ID
        self.service_id = settings.CLICK_SERVICE_ID
        self.secret_key = settings.CLICK_SECRET_KEY

    def _verify_sign(self, params: dict) -> bool:
        if not self.secret_key:
            return False
        sign_string = (
            f"{params.get('click_trans_id')}"
            f"{params.get('service_id')}"
            f"{self.secret_key}"
            f"{params.get('merchant_trans_id')}"
            f"{params.get('amount')}"
            f"{params.get('action')}"
            f"{params.get('sign_time')}"
        )
        expected = hashlib.md5(sign_string.encode()).hexdigest()
        return params.get("sign_string") == expected

    async def create_transaction(self, params: dict) -> dict:
        return await self.prepare(params)

    async def check_transaction(self, params: dict) -> dict:
        return await self.complete(params)

    async def prepare(self, params: dict) -> dict:
        try:
            click_trans_id = params.get("click_trans_id")
            merchant_trans_id = params.get("merchant_trans_id")
            amount = params.get("amount")

            logger.info(
                f"Click Prepare: click_id={click_trans_id}, "
                f"merchant_id={merchant_trans_id}, amount={amount}"
            )

            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_prepare_id": merchant_trans_id,
                "error": 0,
                "error_note": "Success",
            }
        except Exception as e:
            logger.error(f"Click Prepare error: {e}")
            raise AppError("Click tayyorlash xatosi", status_code=500)

    async def complete(self, params: dict) -> dict:
        try:
            click_trans_id = params.get("click_trans_id")
            merchant_trans_id = params.get("merchant_trans_id")
            merchant_prepare_id = params.get("merchant_prepare_id")

            logger.info(
                f"Click Complete: click_id={click_trans_id}, "
                f"merchant_id={merchant_trans_id}"
            )

            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_confirm_id": merchant_prepare_id,
                "error": 0,
                "error_note": "Success",
            }
        except Exception as e:
            logger.error(f"Click Complete error: {e}")
            raise AppError("Click yakunlash xatosi", status_code=500)


class UzumGateway(BaseGateway):
    """Uzum (Apelsin) payment gateway integration."""

    def __init__(self):
        self.merchant_id = settings.UZUM_MERCHANT_ID
        self.secret_key = settings.UZUM_SECRET_KEY

    def _verify_signature(self, signature: Optional[str], body: bytes) -> bool:
        if not self.secret_key or not signature:
            return False
        import hmac

        expected = hmac.new(
            self.secret_key.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    async def create_transaction(self, params: dict) -> dict:
        try:
            transaction_id = params.get("transactionId")
            amount = params.get("amount")
            invoice_id = params.get("invoiceId")

            logger.info(
                f"Uzum CreateTransaction: id={transaction_id}, "
                f"amount={amount}, invoice={invoice_id}"
            )

            return {
                "serviceId": self.merchant_id,
                "transactionId": transaction_id,
                "status": 0,
                "create_time": int(time.time() * 1000),
            }
        except Exception as e:
            logger.error(f"Uzum CreateTransaction error: {e}")
            raise AppError("Uzum tranzaksiya xatosi", status_code=500)

    async def check_transaction(self, params: dict) -> dict:
        try:
            transaction_id = params.get("transactionId")

            logger.info(f"Uzum CheckTransaction: id={transaction_id}")

            return {
                "serviceId": self.merchant_id,
                "transactionId": transaction_id,
                "status": 0,
                "create_time": int(time.time() * 1000),
            }
        except Exception as e:
            logger.error(f"Uzum CheckTransaction error: {e}")
            raise AppError("Uzum tekshiruv xatosi", status_code=500)

    async def confirm_transaction(self, params: dict) -> dict:
        try:
            transaction_id = params.get("transactionId")

            logger.info(f"Uzum ConfirmTransaction: id={transaction_id}")

            return {
                "serviceId": self.merchant_id,
                "transactionId": transaction_id,
                "status": 1,
                "confirm_time": int(time.time() * 1000),
            }
        except Exception as e:
            logger.error(f"Uzum ConfirmTransaction error: {e}")
            raise AppError("Uzum tasdiqlash xatosi", status_code=500)

    async def reverse_transaction(self, params: dict) -> dict:
        try:
            transaction_id = params.get("transactionId")

            logger.info(f"Uzum ReverseTransaction: id={transaction_id}")

            return {
                "serviceId": self.merchant_id,
                "transactionId": transaction_id,
                "status": -1,
                "reverse_time": int(time.time() * 1000),
            }
        except Exception as e:
            logger.error(f"Uzum ReverseTransaction error: {e}")
            raise AppError("Uzum qaytarish xatosi", status_code=500)
