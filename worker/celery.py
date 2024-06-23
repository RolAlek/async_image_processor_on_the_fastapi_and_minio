from celery import Celery

from app.core.config import settings


app = Celery(
    'worker',
    broker=settings.celery.broker,
    backend=settings.celery.backend,
)
