from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.crud.image import create_image
from app.services.utils import wait_create_url_task
from app.schemas.image import ImageRequest, ImageResponse
from worker.tasks import upload_image_via_presigned_url, generate_presigned_url


router = APIRouter(prefix='/images', tags=['Image'])


@router.post('/', response_model=ImageResponse)
async def create_image_view(
    request: ImageRequest,
    session: AsyncSession = Depends(db.get_session),
):
    # Создаем экземпляр Image в БД:
    image_db = await create_image(request, session)
    # Запускаем задачу в celery по генерации presigned_url:
    task = generate_presigned_url.delay(
        project_id=image_db.project_id,
        filename=image_db.filename,
    )
    # Асинхронная проверка задачи и получения результата, в цикле событий
    # ждем ссылку:
    task_result = await wait_create_url_task(AsyncResult(task.id))

    if task_result:
        # upload_image_via_presigned_url.delay(task_result, await image.read())
        return ImageResponse(
            upload_link=task_result.get('url'),
            params=task_result.get('fields')
        )
