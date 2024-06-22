from sqlalchemy.ext.asyncio import AsyncSession
import requests


from app.services.s3_service import create_presigned_upload_url
from worker.main_worker import celery_app

# TODO: Успешный код - статус у Image upload + получи ссылку из minio и положи ее в original

@celery_app.task
def upload_image_via_presigned_url(response, file_content):
    response = requests.post(
        url=response['url'],
        data=response['fields'],
        files={'file': file_content}
    )
    if response.status_code == 204:
        pass


@celery_app.task
def generate_presigned_url(project_id: int, filename: str):
    response = create_presigned_upload_url(
        project_id=project_id,
        filename=filename,
    )
    return response


@celery_app.task
def get_link_end_set_state(s3_client, session: AsyncSession):
    pass
