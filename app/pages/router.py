from fastapi import APIRouter, Depends, Form, Request
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
    session: AsyncSession = Depends(db.get_session),
):
    result: ImageResponse | None = await create_image_view(
        request=ImageRequest(
            filename=filename,
            project_id=project_id,
        ),
        session=session,
    )
    result = result.model_dump()
    request.session['upload_url'] = {
        'url': result['upload_link'],
        'fields': result['params'],
    }
    return RedirectResponse(url='image_upload')


@router.post('/image_upload', response_class=HTMLResponse)
async def image_upload(request: Request):
    upload_url = request.session.get('upload_url')
    return templates.TemplateResponse(
        'upload.html',
        {
            'request': request,
            'fields': upload_url['fields'],
        }
    )
