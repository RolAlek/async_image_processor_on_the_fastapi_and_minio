from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.crud.image import create_image
from app.schemas.image import ImageRequest, ImagesResponse
from app.services.utils import task_manager

router = APIRouter(prefix='/images', tags=['Image'])


@router.post('/', response_model=ImagesResponse)
async def create_image_view(
    image: ImageRequest,
    websocket: WebSocket,
    session: AsyncSession = Depends(db.get_session),
):
    image_db = await create_image(image, session)
    result = await task_manager(
        image.image,
        image.filename,
        image.project_id,
        image_db,
        session,
        websocket,
    )

    return result
