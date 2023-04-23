import logging
import struct
from uuid import uuid4
from fastapi_mqtt import FastMQTT, MQTTConfig
from gmqtt.mqtt.constants import MQTTv311
from .operations import ImageDataInput, system_write_images
from .utils import get_cluster_ip_address

log = logging.getLogger(__name__)

mqtt = FastMQTT(
    config=MQTTConfig(
        host=get_cluster_ip_address('rabbitmq-cluster.rabbitmq-cluster.svc.cluster.local'),
        port=1883,
        username='kamera-cloud',
        password='kamera-cloud',
        version=MQTTv311
    )
)

@mqtt.subscribe("amq/topic")
async def on_receive_image_data(client, topic, payload, qos, properties):
    image_size = int.from_bytes(payload[0:4], 'big')
    unpack_data = struct.unpack('>LLQ4s{image_size}B'.format(image_size = image_size), payload)
    _, camera_id, timestamp_ms, image_format = unpack_data[0:4]
    image_format = image_format.decode('utf-8')
    image_data = bytes(unpack_data[4:])

    writeData: ImageDataInput = {
        'camera_id': camera_id,
        'timestamp_ms': timestamp_ms,
        'file_name': '{uuid}.{image_format}'.format(uuid = uuid4(), image_format = image_format.replace('.', '')),
        'byte_data': image_data,
    }

    system_write_images([writeData])

def init_app_mqtt(app) -> None:
    mqtt.init_app(app)
