from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.crud.project import get_project_images
from app.schemas.image import ProjectImages, ProjectResponse, ImageVersions


router = APIRouter(prefix='/projects', tags=['Project'])


@router.get('/{id}/images', response_model=ProjectResponse)
async def get_images_for_project(
    id: int,
    session: AsyncSession = Depends(db.get_session),
):
    project = await get_project_images(id, session)

    images_response = [
        ProjectImages(
            image_id=image.id,
            state=image.state,
            filename=image.filename,
            project_id=image.project_id,
            versions=ImageVersions(
                original=image.original,
                thumb=image.thumb,
                big_thumb=image.big_thumb,
                big_1920=image.big_1920,
                d2500=image.d2500,
            )
        )
        for image in project.images
    ]
    return ProjectResponse(images=images_response)
