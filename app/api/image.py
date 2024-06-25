from celery.result import AsyncResult
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.crud.image import create_image
from app.services.utils import wait_task
from app.schemas.image import ImageRequest, ImageResponse
from worker.tasks import image_processor, upload_images


router = APIRouter(prefix='/images', tags=['Image'])


@router.post('/', response_model=ImageResponse)
async def create_image_view(
    request: ImageRequest,
    session: AsyncSession = Depends(db.get_session),
):
    # Создаем экземпляр Image в БД:
    image_db = await create_image(request, session)
    # Запускаем задачу в celery по генерации presigned_url:
    processing = image_processor.delay(await request.image.read(), image_db.filename)
    # Асинхронная проверка задачи и получения результата, в цикле событий
    # ждем ссылку:
    processing_result = await wait_task(AsyncResult(processing.id))

    uploading = upload_images.delay(request.project_id, processing_result)
    upload_result = await wait_task(AsyncResult(uploading.id))
    return upload_result
