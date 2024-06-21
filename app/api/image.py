from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core import db
from crud.image import create_image
from schemas.image import ImageRequest, ImageResponse
from services.s3_service import create_presigned_upload_url


router = APIRouter(prefix='/images', tags=['Image'])


@router.post('/', response_model=ImageResponse)
async def create_image_view(
    request: ImageRequest,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(db.get_session),
):
    image = await create_image(request, session)
    s3_response = create_presigned_upload_url(
        project_id=image.project_id,
        filename=image.filename,
    )
    if s3_response:
        return ImageResponse(upload_link=s3_response.get('url'), params=s3_response.get('fields'))

