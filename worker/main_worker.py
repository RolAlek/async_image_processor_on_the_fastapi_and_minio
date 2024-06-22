import os

from dotenv import load_dotenv
from celery import Celery

load_dotenv('.env')


celery_app = Celery(
    'lite_gallery',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_BACKEND_URL'),
)
