from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from . import Base

if TYPE_CHECKING:
    from . import Image


class Project(Base):
    images: Mapped[list['Image']] = relationship(back_populates='project')
