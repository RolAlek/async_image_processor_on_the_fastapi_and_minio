from celery.result import AsyncResult
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.crud.image import create_image, update_image
from app.services.utils import wait_task
from app.schemas.image import ImageRequest, ImageResponse, ImageVersions
from worker.tasks import image_processor, upload_images


router = APIRouter(prefix='/images', tags=['Image'])


@router.post('/', response_model=ImageResponse)
async def create_image_view(
    request: ImageRequest,
    session: AsyncSession = Depends(db.get_session),
):
    # Создаем экземпляр Image в БД:
    image_db = await create_image(request, session)
    # Запускаем обработку в celery:
    processing = image_processor.delay(
        await request.image.read(),
        image_db.filename,
    )
    # Асинхронно ждем результат обработки и меняем статус на processed:
    processing_result = await wait_task(AsyncResult(processing.id))
    image_db = await update_image(
        image=image_db,
        session=session,
        state='processed',
    )
    # По аналогии с обработкой
    uploading = upload_images.delay(request.project_id, processing_result)
    upload_result = await wait_task(AsyncResult(uploading.id))
    image = await update_image(
        image_db,
        session,
        ImageVersions(**upload_result),
        'uploaded'
    )
    return upload_result
