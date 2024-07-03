from fastapi import File, UploadFile
from pydantic import BaseModel, Field


class ImageRequest(BaseModel):
    filename: str
    project_id: int
    image: UploadFile = File(...)


class ImageVersions(BaseModel):
    original: str | None
    thumb: str | None
    big_thumb: str | None
    big_1920: str | None
    d2500: str | None


class ImagesResponse(BaseModel):
    id: int = Field(..., alias='image_id')
    state: str
    filename: str
    project_id: int
    versions: ImageVersions

    class Config:
        orm_mode = True


class ProjectResponse(BaseModel):
    images: list[ImagesResponse]
