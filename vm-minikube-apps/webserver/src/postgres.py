import logging
from typing import Optional, TypedDict
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from .utils import get_cluster_ip_address

log = logging.getLogger(__name__)

class ImageMetadataEntry(TypedDict):
    camera_id: int
    image_timestamp: int
    image_format: str
    bucket_url: str

# Improve performance by caching database connections instead of creating new connections for every database operation
connection_pool = ConnectionPool(
    'host={host} port={port} user={user} password={password} dbname={dbname}'
        .format(
            host = get_cluster_ip_address('postgres-server.postgres.svc.cluster.local'),
            port = 5432,
            user = 'shaysrebellion',
            password = 'postgresdb',
            dbname = 'image_metadata',
        )
    )

def get_db_image_metadata(camera_id: Optional[int], image_type: Optional[str], timestamp_ms_lower: int, timestamp_ms_upper: int) -> list[ImageMetadataEntry]:
    query = ' \
        SELECT * FROM image_metadata \
        WHERE {camera_id_condition} {timestamp_lower_condition} {timestamp_upper_condition} {image_type_condition} \
        ORDER BY camera_id, timestamp, image_type ASC \
    '.format(
        camera_id_condition = 'camera_id = {} AND'.format(camera_id) if camera_id else '',
        timestamp_lower_condition = 'timestamp >= {} AND'.format(timestamp_ms_lower),
        timestamp_higher_condition = 'timestamp <= {} AND'.format(timestamp_ms_upper),
        image_type_condition = 'image_type = {}'.format(image_type) if image_type else '',
    )

    with connection_pool.connection() as conn:
        with conn.cursor(row_factory = dict_row) as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
    return data

def set_db_image_metadata(data: list[ImageMetadataEntry]) -> None:
    tuple_data = [tuple(entry.values()) for entry in data]
    with connection_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO image_metadata VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                tuple_data
            )
            conn.commit()
