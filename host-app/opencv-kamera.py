import struct
import time
import paho.mqtt.client as mqtt
from opencv_kamera_types import ImageColor, ImageFormat
from opencv_kamera import OpenCvCamera

def prompt_user_image_info(info: str, infoEnumClass) -> str:
    image_info = ''
    is_valid = False
    while not is_valid:
        try:
            user_input = input('Image {}: '.format(info))
            enum_value = infoEnumClass(user_input)
            is_valid = True
            image_info = enum_value.value
        except Exception as e:
            print('Valid image {}: {}'.format(info, [entry.value for entry in infoEnumClass if not entry == ImageFormat.RAW]).replace("'", ""))
    return image_info

def main():
    mqttc = mqtt.Client(protocol=mqtt.MQTTv311)
    mqttc.username_pw_set('kamera-cloud', 'kamera-cloud')
    mqttc.connect('mqtt.kamera-cloud-rabbitmq.io', 30000)
    mqttc.loop_start()

    camera = OpenCvCamera()
    end_session = False

    while not end_session:
        image_color = prompt_user_image_info('color', ImageColor)
        image_format = prompt_user_image_info('format', ImageFormat)

        _, image = camera.snap_image(ImageColor(image_color), ImageFormat(image_format))
        data_pack = struct .pack( '>LLQ4s{image_size}B'.format(image_size = len(image)), len(image), 0, round(time.time() * 1000), bytes(image_format, 'utf-8'), *image.tobytes())
        mqttc.publish('amq/topic', data_pack)

        end_session = input('End session (y/N): ')[0].lower() == 'y'

    mqttc.loop_stop()
    mqttc.disconnect()

if __name__ == '__main__':
    main()
