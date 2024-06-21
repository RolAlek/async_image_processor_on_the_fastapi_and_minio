from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.crud.image import create_image
from app.schemas.image import ImageRequest, ImageResponse
from app.services.s3_service import create_presigned_upload_url
from worker.tasks import upload_image_via_presigned_url


router = APIRouter(prefix='/images', tags=['Image'])


@router.post('/', response_model=ImageResponse)
async def create_image_view(
    filename: str = Form(...),
    project_id: int = Form(...),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(db.get_session),
):
    image_db = await create_image(
        ImageRequest(
            filename=filename,
            project_id=project_id
        ),
        session,
    )
    s3_response = create_presigned_upload_url(
        project_id=image_db.project_id,
        filename=image_db.filename,
    )
    file_content = await image.read()
    upload_image_via_presigned_url.delay(s3_response, file_content)
    if s3_response:
        return ImageResponse(
            upload_link=s3_response.get('url'),
            params=s3_response.get('fields')
        )
