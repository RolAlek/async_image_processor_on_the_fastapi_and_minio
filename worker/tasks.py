import requests
from io import BytesIO

from PIL import Image

from app.services.image_processing import resize_image
from app.services.s3_service import (
    create_presigned_download_url,
    create_presigned_upload_url,
    check_exists_object,
)
from worker.celery import app


FORMATS = [
    {'name': 'original'},
    {'name': 'thumb', 'width': 150, 'height': 120},
    {'name': 'big_thumb', 'width': 700, 'height': 700},
    {'name': 'big_1920', 'width': 1920, 'height': 1080},
    {'name': 'd2500', 'width': 2500, 'height': 2500}
]



@app.task
def upload_image_via_presigned_url(presigned_post_result, images):
    #  FIXME: Почему то сохраняет изображение только в одной версии - скорее всего надо генерировать ссылку на каждую отдельно
    url = presigned_post_result['upload_link']
    fields = presigned_post_result['params']
    image_downloads_urls = {}
    for key, value in images.items():
        response = requests.post(
            url=url,
            data=fields,
            files={'file': value},
        )
        if response.status_code == 204:
            bucket = url.split('/')[-1]
            key = fields['key']
            if check_exists_object(bucket, key):
                download_url = create_presigned_download_url(bucket, key)
                if download_url is not None:
                    image_downloads_urls[key] = download_url
    return image_downloads_urls


@app.task
def generate_presigned_url(project_id: int, filename: str):
    response = create_presigned_upload_url(
        project_id=project_id,
        filename=filename,
    )
    return response


@app.task
def image_processor(image):
    image_versions = {}

    for frmt in FORMATS:
        if frmt['name'] == 'original':
            image_versions['original'] = image
            continue
        original_image = Image.open(BytesIO(image))
        resized_image = resize_image(
            original_image,
            frmt['width'],
            frmt['height']
        )
        buffer = BytesIO()
        resized_image.save(buffer, format=original_image.format)
        image_versions[f'{frmt["name"]}'] = buffer.getvalue()
    return image_versions
