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
    {'name': 'original', 'width': 0, 'height': 0},
    {'name': 'thumb', 'width': 150, 'height': 120},
    {'name': 'big_thumb', 'width': 700, 'height': 700},
    {'name': 'big_1920', 'width': 1920, 'height': 1080},
    {'name': 'd2500', 'width': 2500, 'height': 2500}
]
NEW_FILE_NAME = '{name}_{version}.{frmt}'



@app.task
def upload_images(project_id:int, images: list):
    result = {}
    for image in images:
        for name, version in image.items():
            image_name, frmt = name.split('.')
            file_name = NEW_FILE_NAME.format(
                name=image_name,
                version=version['version'],
                frmt=frmt
            )
            presigned_dict = create_presigned_upload_url(project_id, file_name)
            url = presigned_dict['url']
            fields = presigned_dict['fields']
            response = requests.post(
                url=url,
                data=fields,
                files={'file': version['image']},
            )
            if response.status_code == 204:
                bucket = url.split('/')[-1]
                key = fields['key']
                if check_exists_object(bucket, key):
                    download_url = create_presigned_download_url(bucket, key)
                    if download_url is not None:
                        result[version['version']] = download_url
    return result


@app.task
def image_processor(image, image_name) -> list[dict[str]]:
    original_image = Image.open(BytesIO(image))
    image_versions = []
    frmt = original_image.format
    image_name = f'{image_name}.{frmt.lower()}'

    for version in FORMATS:
        temp = {}
        temp[image_name] = {}
        temp[image_name]['version'] = version['name']
        if version['name'] == 'original':
            resized_image = original_image
        else:
            resized_image = resize_image(
                original_image,
                version['width'],
                version['height']
            )
        buffer = BytesIO()
        resized_image.save(buffer, format=frmt)
        temp[image_name]['image'] = buffer.getvalue()
        image_versions.append(temp)
    return image_versions
