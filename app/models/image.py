from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from . import Base

if TYPE_CHECKING:
    from . import Project


class StateEnum(str, PyEnum):
    INIT = 'init'
    UPLOADED = 'uploaded'
    PROCESSING = 'processing'
    DONE = 'done'
    ERROR = 'error'


class Image(Base):
    filename: Mapped[str]
    state:  Mapped[StateEnum] = mapped_column(
        Enum(StateEnum), default=StateEnum.INIT.value
    )
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'))
    #vesrions
    original: Mapped[str | None]
    thumb: Mapped[str | None]
    big_thumb: Mapped[str | None]
    big_1920: Mapped[str | None]
    d2500: Mapped[str | None]
