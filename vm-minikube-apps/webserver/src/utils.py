import logging
import subprocess
from .aws import AWS_REGION, AWS_S3_BUCKET

log = logging.getLogger(__name__)

# for some reason will not automatically resolve to IP address, so manually input IP
def get_cluster_ip_address(hostname: str) -> str:
    cmd =  "getent hosts " + hostname + " | awk '{ print $1 }'"
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode()[0: -1]

def get_aws_url_from_file_name(file_name: str) -> str:
    return 'https://{bucket}.s3.{region}.amazonaws.com/{file_name}'.format(bucket = AWS_S3_BUCKET, region = AWS_REGION, file_name = file_name)

def get_file_name_from_aws_url(aws_url: str) -> str:
    return aws_url[(aws_url.rfind('/') + 1):]

def get_extension(file: str):
    return file[(file.rfind('.') + 1):]
