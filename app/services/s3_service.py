from boto3 import client, session
from botocore.exceptions import ClientError

from app.core.config import settings


def create_s3_client():
    s3_client = client(
        's3',
        endpoint_url=settings.minio.endpoint,
        aws_access_key_id = settings.minio.access_key,
        aws_secret_access_key = settings.minio.secret_key,
        config=session.Config(signature_version='s3v4'),
    )
    return s3_client


def check_exist_bucket(project_id: int, s3_client):
    try:
        bucket_name = f'project-{project_id}'
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as error:
        if error.response['Error']['Code'] == '404':
            s3_client.create_bucket(Bucket=bucket_name)
            return bucket_name
    return bucket_name


def create_presigned_upload_url(
    project_id: int,
    file_name: str,
    fields: dict | None = None,
    conditions: list | None = None,
    expiration: int = 3600,
):
    try:
        s3_client = create_s3_client()
        bucket_name = check_exist_bucket(project_id, s3_client)
        response = s3_client.generate_presigned_post(
            bucket_name,
            file_name,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expiration,
        )
    except ClientError:
        return None
    return response


def check_exists_object(bucket: str, key: str):
    s3_client = create_s3_client()
    try:
        s3_client.head_object(
            Bucket=bucket,
            Key=key,
        )
    except ClientError:
        return False
    return True


def create_presigned_download_url(
    bucket_name: str,
    object_name: str,
    expiration: int =3600
):
    s3_client = create_s3_client()
    try:
        response = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=expiration,
        )
    except ClientError:
        return None
    return response
