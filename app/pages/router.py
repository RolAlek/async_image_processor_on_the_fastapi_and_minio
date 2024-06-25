from fastapi import APIRouter, Depends, Form, File, Request, UploadFile, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.api.image import create_image_view
from app.schemas.image import ImageRequest, ImageResponse



router = APIRouter(prefix='/pages', tags=['Pages'])

templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})



@router.post('/image_create', response_class=RedirectResponse)
async def image_create(
    request: Request,
    filename: str = Form(...),
    project_id: int = Form(...),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(db.get_session),
):
    result: ImageResponse | None = await create_image_view(
        request=ImageRequest(
            filename=filename,
            project_id=project_id,
            image=image,
        ),
        session=session,
    )
    return templates.TemplateResponse(
        'project.html', {'request': request, 'images': result}
    )
