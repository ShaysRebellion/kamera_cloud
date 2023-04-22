import json
import uuid

from fastapi_mqtt import FastMQTT, MQTTConfig
from gmqtt.mqtt.constants import MQTTv311

from .aws import AwsObjectData, AwsOperationResult, upload_files
from .postgres import ImageMetadataEntry, set_image_metadata
from .redis import set_image_data
from .utils import get_cluster_ip_address

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

    # set_image_metadata([{
    #     'camera_id': data['camera_id'],
    #     'image_timestamp': data['timestamp_ms'],
    #     'image_format': data['image_format'],
    #     'bucket_url': '',
    # }])

    # set_image_data()

def init_app_mqtt(app) -> None:
    mqtt.init_app(app)
