import io
import logging
import os
from typing import TypedDict
import boto3

log = logging.getLogger(__name__)

class AwsObjectData(TypedDict):
    object_name: str
    byte_data: bytes

class AwsOperationResult(TypedDict):
    object_name: str
    result: bool

S3_CLIENT = boto3.client('s3')
AWS_S3_BUCKET = os.environ.get('AWS_S3_IMAGE_BUCKET', 'kamera-cloud-image-bucket')
AWS_REGION = os.environ.get('AWS_S3_IMAGE_BUCKET_REGION', 'ap-northeast-1')

def upload_bucket_files(data: list[AwsObjectData]) -> list[AwsOperationResult]:
    operation_results: list[AwsOperationResult] = []
    for entry in data:
        result: AwsOperationResult = AwsOperationResult(object_name=entry['object_name'], result=False)
        try:
            S3_CLIENT.upload_fileobj(io.BytesIO(entry['byte_data']), AWS_S3_BUCKET, entry['object_name'])
        except Exception as e:
            log.warn(e)
            result['result'] = False
        finally:
            operation_results.append(result)
    return operation_results

def download_bucket_files(object_names: list[str]) -> list[AwsObjectData]:
    data_aggregate: list[AwsObjectData] = []
    for name in object_names:
        bytes_buffer = io.BytesIO()
        try:
            S3_CLIENT.download_fileobj(AWS_S3_BUCKET, name, bytes_buffer)
        except Exception as e:
            log.warn(e)
        finally:
            data_aggregate.append(AwsObjectData(object_name=name, byte_data=bytes_buffer.read()))
    return data_aggregate
