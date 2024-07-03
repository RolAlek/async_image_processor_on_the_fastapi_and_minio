from io import BytesIO

from PIL import Image
import requests
from requests.exceptions import RequestException



from app.services.image_processing import resize_image
from app.services.s3_service import (check_exists_object,
                                     create_presigned_download_url,
                                     create_presigned_upload_url)
from worker.celery import app

FORMATS = [
    {'name': 'original', 'width': 0, 'height': 0},
    {'name': 'thumb', 'width': 150, 'height': 120},
    {'name': 'big_thumb', 'width': 700, 'height': 700},
    {'name': 'big_1920', 'width': 1920, 'height': 1080},
    {'name': 'd2500', 'width': 2500, 'height': 2500}
]
NEW_FILE_NAME = '{name}_{version}.{frmt}'


@app.task(name='downloading')
def image_downloader(bucket: str, key: str):
    if not check_exists_object(bucket, key):
        return
    download_url = create_presigned_download_url(bucket, key)
    if download_url is not None:
        return key, download_url


@app.task(name='uploading')
def image_uploader(project_id: int, image_name: str, image: bytes):
    upload_params = create_presigned_upload_url(project_id, image_name)
    if upload_params is None:
        return
    url = upload_params['url']
    fields = upload_params['fields']
    response = requests.post(
        url=url,
        data=fields,
        files={'file': image},
        timeout=3,
    )
    if response.status_code == 204:
        return url.split('/')[-1], fields['key']


@app.task(name='processing')
def image_processor(
    image: bytes,
    image_name: str,
    version: dict[str, str | int]
) -> tuple[str, bytes]:
    with Image.open(BytesIO(image)) as original_image:
        frmt = original_image.format
        image_name = NEW_FILE_NAME.format(
            name=image_name,
            version=version['name'],
            frmt=frmt,
        )
        if version['name'] != 'original':
            resized_image = resize_image(
                original_image,
                version['width'],
                version['height'],
            )
        else:
            resized_image = original_image
        buffer = BytesIO()
        resized_image.save(buffer, format=frmt)
        buffer.getvalue()

    return image_name, buffer.getvalue()
