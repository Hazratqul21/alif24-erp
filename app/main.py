import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import sentry_sdk

from app.config import settings
from app.core.database import init_public_schema
from app.core.tenant import TenantMiddleware
from app.core.exceptions import AppError

from app.api.v1 import (
    auth, users, roles, students, teachers, parents,
    academic, schedule, attendance, grades, payments,
    library, medical, psychology, discipline,
    canteen, transport, notifications, documents,
    competitions, rooms, homework, exams, admissions,
    portfolio, surveys, reports, audit, holidays,
    alif24_integration, upload,
)
from app.api.v1.superadmin import (
    tenants as sa_tenants,
    plans as sa_plans,
    monitoring as sa_monitoring,
    audit as sa_audit,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Alif24 School ERP ishga tushmoqda...")
    await init_public_schema()
    logger.info("Public schema tayyor")
    yield
    logger.info("Alif24 School ERP to'xtamoqda...")


if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)

app = FastAPI(
    title="Alif24 School ERP",
    version="1.0.0",
    description="Multi-tenant maktab boshqaruv tizimi",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TenantMiddleware)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception(f"Kutilmagan xatolik: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Ichki server xatosi"})


PREFIX = settings.API_PREFIX

app.include_router(auth.router, prefix=f"{PREFIX}/auth", tags=["Auth"])
app.include_router(users.router, prefix=f"{PREFIX}/users", tags=["Users"])
app.include_router(roles.router, prefix=f"{PREFIX}", tags=["Roles & Permissions"])
app.include_router(students.router, prefix=f"{PREFIX}/students", tags=["Students"])
app.include_router(teachers.router, prefix=f"{PREFIX}/teachers", tags=["Teachers"])
app.include_router(parents.router, prefix=f"{PREFIX}/parents", tags=["Parents"])
app.include_router(academic.router, prefix=f"{PREFIX}/academic", tags=["Academic"])
app.include_router(schedule.router, prefix=f"{PREFIX}/schedules", tags=["Schedule"])
app.include_router(attendance.router, prefix=f"{PREFIX}/attendance", tags=["Attendance"])
app.include_router(grades.router, prefix=f"{PREFIX}/grades", tags=["Grades"])
app.include_router(payments.router, prefix=f"{PREFIX}/payments", tags=["Payments"])
app.include_router(library.router, prefix=f"{PREFIX}/library", tags=["Library"])
app.include_router(medical.router, prefix=f"{PREFIX}/medical", tags=["Medical"])
app.include_router(psychology.router, prefix=f"{PREFIX}/psychology", tags=["Psychology"])
app.include_router(discipline.router, prefix=f"{PREFIX}/discipline", tags=["Discipline"])
app.include_router(canteen.router, prefix=f"{PREFIX}/canteen", tags=["Canteen"])
app.include_router(transport.router, prefix=f"{PREFIX}/transport", tags=["Transport"])
app.include_router(notifications.router, prefix=f"{PREFIX}/notifications", tags=["Notifications"])
app.include_router(documents.router, prefix=f"{PREFIX}/documents", tags=["Documents"])
app.include_router(competitions.router, prefix=f"{PREFIX}/competitions", tags=["Competitions"])
app.include_router(rooms.router, prefix=f"{PREFIX}/rooms", tags=["Rooms"])
app.include_router(homework.router, prefix=f"{PREFIX}/homework", tags=["Homework"])
app.include_router(exams.router, prefix=f"{PREFIX}/exams", tags=["Exams"])
app.include_router(admissions.router, prefix=f"{PREFIX}/admissions", tags=["Admissions"])
app.include_router(portfolio.router, prefix=f"{PREFIX}/portfolio", tags=["Portfolio"])
app.include_router(surveys.router, prefix=f"{PREFIX}/surveys", tags=["Surveys"])
app.include_router(reports.router, prefix=f"{PREFIX}/reports", tags=["Reports"])
app.include_router(audit.router, prefix=f"{PREFIX}/audit", tags=["Audit"])
app.include_router(holidays.router, prefix=f"{PREFIX}/holidays", tags=["Holidays"])
app.include_router(alif24_integration.router, prefix=f"{PREFIX}", tags=["Alif24 Integration"])
app.include_router(upload.router, prefix=f"{PREFIX}/upload", tags=["Upload"])

app.include_router(sa_tenants.router, prefix=f"{PREFIX}/superadmin/tenants", tags=["Super Admin - Tenants"])
app.include_router(sa_plans.router, prefix=f"{PREFIX}/superadmin/plans", tags=["Super Admin - Plans"])
app.include_router(sa_monitoring.router, prefix=f"{PREFIX}/superadmin/monitoring", tags=["Super Admin - Monitoring"])
app.include_router(sa_audit.router, prefix=f"{PREFIX}/superadmin/audit", tags=["Super Admin - Audit"])


static_uploads = "/app/static/uploads"
try:
    os.makedirs(static_uploads, exist_ok=True)
except PermissionError:
    import logging
    logging.getLogger(__name__).warning(
        "Cannot create %s (permission denied). File uploads will fail until the directory is writable.",
        static_uploads,
    )

if os.path.isdir(static_uploads):
    app.mount("/static/uploads", StaticFiles(directory=static_uploads), name="uploads")


@app.get("/", tags=["Health"])
async def root():
    return {"service": "Alif24 School ERP", "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
