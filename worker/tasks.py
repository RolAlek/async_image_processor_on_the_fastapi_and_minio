import requests

from worker.main_worker import celery_app

# TODO: Проверь статус код
# TODO: Успешный код - статус у Image upload + получи ссылку из minio и положи ее в original

@celery_app.task
def upload_image_via_presigned_url(response, file_content):
    response = requests.post(
        url=response['url'],
        data=response['fields'],
        files={'file': file_content}
    )
    print(response.status_code)
