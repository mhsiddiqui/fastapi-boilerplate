from celery import Celery
from .config import settings


celery_app = Celery("worker")

celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND
celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
