from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession


from app.models import Image, Project, StateEnum
from app.schemas.image import ImageRequest, ImageVersions


async def check_and_create_project(
    project_id: int,
    session: AsyncSession,
) -> Project:
    project = await session.get(Project, project_id)
    if not project:
        new_project = Project(id=project_id)
        session.add(new_project)
        await session.commit()
        await session.refresh(new_project)
        return new_project
    return project


async def create_image(request: ImageRequest, session: AsyncSession):
    data = request.model_dump()
    await check_and_create_project(data['project_id'], session)
    image = Image(filename=data['filename'], project_id=data['project_id'])
    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image


async def update_image(
    image: Image,
    session: AsyncSession,
    data: ImageVersions | None = None,
    state: str | None = None,
):
    image_data = jsonable_encoder(image)
    if data is not None:
        update_data = data.model_dump()
        for field in image_data:
            if field in update_data:
                setattr(image, field, update_data[field])
    if state is not None:
        setattr(image, 'state', StateEnum(state).name)

    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image
