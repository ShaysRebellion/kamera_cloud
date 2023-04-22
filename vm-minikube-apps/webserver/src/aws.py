import io
import os
from typing import BinaryIO, TypedDict
import boto3

class AwsObjectData(TypedDict):
    object_name: str
    byte_data: BinaryIO

class AwsOperationResult(TypedDict):
    object_name: str
    result: bool

s3_client = boto3.client('s3')
aws_s3_bucket = os.environ.get('AWS_S3_IMAGE_BUCKET', 'kamera-cloud-image-bucket')
aws_region = os.environ.get('AWS_S3_IMAGE_BUCKET_REGION', 'ap-northeast-1')

def aws_url_formation(file_name: str):
    return 'https://{bucket}.s3.{region}.amazonaws.com/{file_name}'.format(bucket = aws_s3_bucket, region = aws_region, file_name = file_name)

def upload_files(data: list[AwsObjectData]) -> list[AwsOperationResult]:
    operation_results: list[AwsOperationResult] = []
    for entry in data:
        result: AwsOperationResult = AwsOperationResult(object_name=entry['object_name'], result=False)
        try:
            s3_client.upload_fileobj(entry['byte_data'], aws_s3_bucket, entry['object_name'])
        except:
            result['result'] = False
        finally:
            operation_results.append(result)
    return operation_results

def download_files(object_names: list[str]) -> list[AwsObjectData]:
    data_aggregate: list[AwsObjectData] = []
    for name in object_names:
        data: AwsObjectData = AwsObjectData(object_name=name, byte_data=io.BytesIO())
        try:
            s3_client.download_fileobj(aws_s3_bucket, name, data['byte_data'])
        except:
            pass
        finally:
            data_aggregate.append(data)
    return data_aggregate
