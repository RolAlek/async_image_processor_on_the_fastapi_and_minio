from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db
from crud.image import create_image
from schemas.image import ImageRequest, ImageResponse


router = APIRouter(prefix='/images', tags=['Image'])


@router.post('/', response_model=ImageResponse)
async def create_image_view(
    request: ImageRequest,
    session: AsyncSession = Depends(db.get_session)
):
    image = await create_image(request, session)
    return ImageResponse(upload_link='ссылка на загрузку изображения', params={'data': 'какие-то параметры'})

