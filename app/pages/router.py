from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Form, File, Request, UploadFile, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.utils import wait_create_url_task
from app.core import db
from app.api.image import create_image_view
from app.api.project import get_images_for_project
from app.schemas.image import ImageRequest, ImageResponse
from worker.tasks import upload_image_via_presigned_url, image_processor



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
    request.session['result'] = result.model_dump()
    request.session['project_id'] = project_id
    return RedirectResponse('image_upload_view')


@router.post('/image_upload_view', response_class=HTMLResponse)
async def image_upload_view(request: Request):
    result = request.session.get('result')
    return templates.TemplateResponse(
        'upload.html',
        {'request': request, 'params': result.get('params')}
    )


@router.post('/image_upload')
async def image_upload(request: Request, image: UploadFile = File(...)):
    task = image_processor.delay(await image.read())
    request.session['task_id'] = task.id
    return RedirectResponse(f'projects/{request.session.get("project_id")}')



@router.post('/projects/{id}', response_class=HTMLResponse)
async def view_project(
    request: Request,
    id: int,
    session: AsyncSession = Depends(db.get_session)
):
    processing_result = await wait_create_url_task(
        AsyncResult(id=request.session.get('task_id')),
    )
    upload_image_via_presigned_url.delay(
        request.session.get('result'),
        processing_result,
    )
    images = await get_images_for_project(id, session)
    return templates.TemplateResponse(
        'project.html',
        {'request': request, 'images': images.model_dump()['images']}
    )
