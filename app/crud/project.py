from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Project


async def get_project_images(id: int, session: AsyncSession):
    stmt = (
        select(Project)
        .where(Project.id == id)
        .options(selectinload(Project.images))
    )
    images = await session.scalars(stmt)
    return images.first()
