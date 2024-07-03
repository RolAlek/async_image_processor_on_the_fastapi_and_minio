import asyncio
from http import HTTPStatus
import re

from celery.result import AsyncResult, states
from fastapi import HTTPException, UploadFile, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.image import update_image
from app.models import StateEnum, Image
from worker.tasks import image_processor, image_uploader, image_downloader


VERSIONS = [
    {'name': 'original', 'width': 0, 'height': 0},
    {'name': 'thumb', 'width': 150, 'height': 120},
    {'name': 'big_thumb', 'width': 700, 'height': 700},
    {'name': 'big_1920', 'width': 1920, 'height': 1080},
    {'name': 'd2500', 'width': 2500, 'height': 2500}
]
PATTERN = '(original|thumb|big_thumb|big_1920|d2500)'


async def task_manager(
    image: UploadFile,
    image_name: str,
    project_id: int,
    image_db: Image,
    session: AsyncSession,
    websocket: WebSocket,
):
    processed_image = await send_for_processing(
        image,
        image_name,
        websocket,
    )
    image_db = await update_image(
        image_db,
        session,
        {'state': StateEnum.PROCESSING.value},
    )

    for item in processed_image:
        bucket, key= await send_for_upload(project_id, item, websocket)
        image_db = await update_image(
            image_db,
            session,
            {'state': StateEnum.UPLOADED.value},
        )
        name, url = await get_download_url(bucket, key, websocket)
        version = re.search(PATTERN, name)
        image_db = await update_image(
            image_db,
            session,
            {'state': StateEnum.DONE.value, version: url},
        )
        return image_db


async def get_download_url(bucket: str, key: str, websocket: WebSocket):
    task = image_downloader.delay(bucket, key)
    return await task_waiter(AsyncResult(task.id), websocket)


async def send_for_upload(
    project_id: int,
    image: tuple[str, bytes],
    websocket: WebSocket
):
    task = image_uploader.delay(project_id, *image)
    result = await task_waiter(AsyncResult(task.id), websocket)
    return result


async def send_for_processing(
    image: UploadFile,
    image_name: str,
    websocket: WebSocket,
) -> list[tuple[str, bytes]]:
    results = []
    for version in VERSIONS:
        task = image_processor.delay(
            await image.read(),
            image_name,
            version,
        )
        processed_image = await task_waiter(
            AsyncResult(task.id),
            websocket
        )
        results.append(processed_image)
    return results


async def task_waiter(
    task: AsyncResult,
    websocket: WebSocket,
    duration: float = 0.5,
):
    # Waiter ждет пока таска не выполнится либо не завершиться ошибкой.
    while task.state not in (states.SUCCESS, states.FAILURE):
        await asyncio.sleep(duration)

    if task.state != states.SUCCESS:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Выполнение "{task.name}" с {task.id} завершилось ошибкой.'
        )
    match task.name:
        case 'processing':
            await websocket.send_text(f'Завершена обработка для {task.result[0]}')
        case 'uploading':
            await websocket.send_text(f'Файл {task.result[1]} загружен в Minio!')
        case 'downloading':
            await websocket.send_json({'image_name': task.result[0], 'url': task.result[-1]})
    return task.result
