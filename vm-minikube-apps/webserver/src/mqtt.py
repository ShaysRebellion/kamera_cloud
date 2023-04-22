import json
import logging
from uuid import uuid4
from fastapi_mqtt import FastMQTT, MQTTConfig
from gmqtt.mqtt.constants import MQTTv311
from opencv_kamera_types import ImageFormat
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

@mqtt.subscribe("amq.topic")
async def on_receive_image_data(client, topic, payload, qos, properties):
    data = json.loads(payload.decode())
    writeData: ImageDataInput = {
        'camera_id': data['camera_id'],
        'timestamp_ms': data['timestamp_ms'],
        'file_name': '{uuid}.{format}'.format(uuid = uuid4(), format = data['image_format'].replace('.', '')),
        'byte_data': data['byte_data']
    }

    log.debug('Payload: {}'.format(payload))
    log.debug('Decoded payload: {}'.format(payload.decode()))
    log.debug('Decoded payload; decoded JSON: {}'.format(data))
    log.debug('WRITE: {}'.format(json.dumps([writeData])))

    # system_write_images([writeData])


def init_app_mqtt(app) -> None:
    mqtt.init_app(app)
