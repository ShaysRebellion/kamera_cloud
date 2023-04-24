import logging
from typing import Any, TypedDict
from redis.cluster import RedisCluster
from .utils import get_cluster_ip_address

log = logging.getLogger(__name__)

class RedisCacheEntry(TypedDict):
    redis_key: str
    data: Any

redis_connection = RedisCluster(
    host=get_cluster_ip_address('redis-cluster.redis-cluster.svc.cluster.local'),
    port=6379,
)

def get_cache_image_data(redis_keys: list[str]):
    pipeline = redis_connection.pipeline()
    for url in redis_keys:
        pipeline.get(url)
    return pipeline.execute() # Note: redis pipeline guarantees execution order

def set_cache_image_data(data: list[RedisCacheEntry]):
    pipeline = redis_connection.pipeline()
    for entry in data:
        pipeline.set(entry['redis_key'], entry['data'])
    return pipeline.execute()
