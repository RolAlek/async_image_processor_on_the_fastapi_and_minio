from sqlalchemy.ext.asyncio import AsyncSession

from models import Image, Project
from schemas.image import ImageRequest


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
    image = Image(**data)
    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image


