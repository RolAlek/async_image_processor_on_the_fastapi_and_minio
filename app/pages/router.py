import base64
import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.image import create_image_view
from app.core import db, manager
from app.schemas.image import ImageRequest, ImagesResponse

router = APIRouter(prefix="/pages", tags=["Pages"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: int,
    session: AsyncSession = Depends(db.get_session),
):
    await manager.connect(websocket, project_id)
    try:
        while True:
            data = await websocket.receive_json()

            result = await create_image_view(
                image=ImageRequest(
                    filename=data["filename"],
                    project_id=data["project_id"],
                    image=data["file"],
                ),
                websocket=websocket,
                session=session,
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
