import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.models import Image
from app.services.s3_service import (
    create_presigned_download_url,
    create_presigned_upload_url,
    check_exists_object,
)
from worker.celery import app

# TODO: Успешный код - статус у Image upload + получи ссылку из minio и положи ее в original

@app.task
def upload_image_via_presigned_url(presigned_post_result, file_content):
    url = presigned_post_result['upload_link']
    fields = presigned_post_result['params']
    response = requests.post(
        url=url,
        data=fields,
        files={'file': file_content},
    )
    if response.status_code == 204:
        bucket = url.split('/')[-1]
        key = fields['key']
        if check_exists_object(bucket, key):
            download_url = create_presigned_download_url(bucket, key)
            if download_url is not None:
                pass


@app.task
def generate_presigned_url(project_id: int, filename: str):
    response = create_presigned_upload_url(
        project_id=project_id,
        filename=filename,
    )
    return response
