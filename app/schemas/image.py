from pydantic import BaseModel, Field


class ImageRequest(BaseModel):
    filename: str
    project_id: int


class ImageResponse(BaseModel):
    upload_link: str
    params: dict


class ImageVersions(BaseModel):
    original: str | None
    thumb: str | None
    big_thumb: str | None
    big_1920: str | None
    d2500: str | None


class ProjectImages(BaseModel):
    id: int = Field(..., alias='image_id')
    state: str
    filename: str
    project_id: int
    versions: ImageVersions


class ProjectResponse(BaseModel):
    images: list[ProjectImages]