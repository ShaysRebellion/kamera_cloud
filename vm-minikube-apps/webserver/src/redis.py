import logging
from typing import TypedDict
from redis.cluster import RedisCluster
from .utils import get_cluster_ip_address

log = logging.getLogger(__name__)

class RedisCacheEntry(TypedDict):
    file_name: str
    bytes_data: bytes

redis_connection = RedisCluster(
    host=get_cluster_ip_address('redis-cluster.redis-cluster.svc.cluster.local'),
    port=6379,
)

def get_cache_image_data(aws_urls: list[str]):
    pipeline = redis_connection.pipeline()
    for url in aws_urls:
        pipeline.get(url)
    return pipeline.execute() # Note: redis pipeline guarantees execution order

def set_cache_image_data(data: list[RedisCacheEntry]):
    pipeline = redis_connection.pipeline()
    for entry in data:
        pipeline.setex(entry['file_name'], 3600, entry['bytes_data'])
    return pipeline.execute()
