import logging
from typing import Optional, TypedDict
from .aws import download_bucket_files, upload_bucket_files
from .postgres import ImageMetadataEntry, get_db_image_metadata, set_db_image_metadata
from .redis import get_cache_image_data, set_cache_image_data
from .utils import get_aws_url_from_file_name, get_file_name_from_aws_url, get_extension

log = logging.getLogger(__name__)

class ImageDataInput(TypedDict):
    camera_id: int
    timestamp_ms: int
    file_name: str
    byte_data: bytes

class ImageData(TypedDict):
    metadata: ImageMetadataEntry
    image_bytes: Optional[bytes]

def system_read_image_metadata(camera_id: Optional[int], image_type: Optional[str], timestamp_ms_lower: int, timestamp_ms_upper: int) -> list[ImageMetadataEntry]:
    redis_key = str(hash((camera_id, image_type, timestamp_ms_lower, timestamp_ms_upper)))
    metadata = get_cache_image_data([redis_key])
    if not metadata: metadata = get_db_image_metadata(camera_id, image_type, timestamp_ms_lower, timestamp_ms_upper)
    set_cache_image_data([{ 'redis_key': redis_key, 'data': metadata }])
    return metadata

def system_read_images(camera_id: Optional[int], image_type: Optional[str], timestamp_ms_lower: int, timestamp_ms_upper: int) -> list[ImageData]:
    image_metadata = system_read_image_metadata(camera_id, image_type, timestamp_ms_lower, timestamp_ms_upper)
    cache_data = get_cache_image_data([get_file_name_from_aws_url(metadata['bucket_url']) for metadata in image_metadata])
    cache_miss_indices = [index for index, data in enumerate(cache_data) if data == None]
    download_result = download_bucket_files([get_file_name_from_aws_url(image_metadata[index]['bucket_url']) for index in cache_miss_indices])
    for index in cache_miss_indices:
        cache_data[index] = download_result[index]

    log.debug('Image_metadata: {}'.format(image_metadata))
    log.debug('Cache miss indices: {}'.format(cache_miss_indices))

    return [{ 'metadata': image_metadata[index], 'image_bytes': data } for index, data in enumerate(cache_data)]

def system_write_images(writeImageDataList: list[ImageDataInput]) -> None:
    upload_result = upload_bucket_files([{ 'object_name': data['file_name'], 'byte_data': data['byte_data'] } for data in writeImageDataList])
    
    upload_fail_indices = [index for index, result in enumerate(upload_result) if not result['result']]
    if len(upload_fail_indices) > 0:
        file_names = [writeImageDataList[index]['file_name'] for index in upload_fail_indices]
        log.warn('Failed to upload files: {file_names}'.format(file_names = file_names))

    # Only write to cache and database for images that successfully uploaded to preserve consistent state
    # In other words, redis cluster server and postgres server should only reflect what's available in bucket
    upload_success_indices = [index for index, result in enumerate(upload_result) if result['result']]
    set_cache_image_data([
        {
            'redis_key': writeImageDataList[index]['file_name'],
            'data': writeImageDataList[index]['byte_data']
        } for index in upload_success_indices
    ])

    set_db_image_metadata([
        {
            'camera_id': writeImageDataList[index]['camera_id'],
            'image_timestamp': writeImageDataList[index]['timestamp_ms'],
            'image_format': get_extension(writeImageDataList[index]['file_name']),
            'bucket_url': get_aws_url_from_file_name(writeImageDataList[index]['file_name'])
        } for index in upload_success_indices
    ])
