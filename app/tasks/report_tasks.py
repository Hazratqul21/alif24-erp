import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="generate_report_cards_task")
def generate_report_cards_task(tenant_id: int, academic_year_id: int, semester: int):
    logger.info(f"Tabellalar yaratilmoqda [tenant={tenant_id}, year={academic_year_id}, semester={semester}]")


@celery_app.task(name="generate_financial_report_task")
def generate_financial_report_task(tenant_id: int, date_from: str, date_to: str):
    logger.info(f"Moliyaviy hisobot [tenant={tenant_id}, {date_from} — {date_to}]")


@celery_app.task(name="export_data_task")
def export_data_task(tenant_id: int, export_type: str, filters: dict):
    logger.info(f"Ma'lumot eksporti [tenant={tenant_id}, type={export_type}]")
