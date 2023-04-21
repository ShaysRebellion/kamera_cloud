from redis.cluster import RedisCluster
from .utils import get_cluster_ip_address

redis_connection = RedisCluster(
    host=get_cluster_ip_address('redis-cluster.redis-cluster.svc.cluster.local'),
    port=6379,
)

def get_image_data(aws_urls):
    pipeline = redis_connection.pipeline()
    for url in aws_urls:
        pipeline.get(url)
    return pipeline.execute()

def set_image_data(aws_urls):
    pipeline = redis_connection.pipeline()
    for url, image in aws_urls.items():
        pipeline.redis_connection.setex(url, 3600, image)
    return pipeline.execute()
