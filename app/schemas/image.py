from pydantic import BaseModel


class ImageRequest(BaseModel):
    filename: str
    project_id: int


class ImageResponse(BaseModel):
    upload_link: str
    params: dict
