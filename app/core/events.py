"""Simple in-process event bus for decoupled notification triggers."""

from typing import Callable, Any
from collections import defaultdict
import asyncio
import logging

logger = logging.getLogger(__name__)

_listeners: dict[str, list[Callable]] = defaultdict(list)


class EventType:
    STUDENT_ABSENT = "student.absent"
    STUDENT_LATE = "student.late"
    GRADE_LOW = "grade.low"
    GRADE_ENTERED = "grade.entered"
    PAYMENT_DUE = "payment.due"
    PAYMENT_RECEIVED = "payment.received"
    HOMEWORK_ASSIGNED = "homework.assigned"
    HOMEWORK_SUBMITTED = "homework.submitted"
    EXAM_SCHEDULED = "exam.scheduled"
    BOOK_OVERDUE = "book.overdue"
    MEDICAL_QUARANTINE = "medical.quarantine"
    BEHAVIOR_INCIDENT = "behavior.incident"
    ANNOUNCEMENT = "announcement"
    USER_CREATED = "user.created"
    TENANT_CREATED = "tenant.created"


def on_event(event_type: str):
    def decorator(func: Callable):
        _listeners[event_type].append(func)
        return func
    return decorator


async def emit_event(event_type: str, data: dict[str, Any], tenant_id: int | None = None):
    payload = {"event": event_type, "tenant_id": tenant_id, "data": data}
    for listener in _listeners.get(event_type, []):
        try:
            if asyncio.iscoroutinefunction(listener):
                await listener(payload)
            else:
                listener(payload)
        except Exception as e:
            logger.error(f"Event listener error [{event_type}]: {e}")
