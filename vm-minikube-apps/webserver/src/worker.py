from argparse import ArgumentParser
import requests
from .operations import system_read_image_metadata

def worker_main():
    parser = ArgumentParser()
    parser.add_argument('--webhook', dest='webhook', type=str, action='store', required=True)
    parser.add_argument('--startMs', dest='start_ms', type=int, action='store', required=True)
    parser.add_argument('--endMs', dest='end_ms', type=int, action='store', required=True)
    parser.add_argument('--cameraId', dest='camera_id', type=int, action='store', default=None)
    parser.add_argument('--format', dest='format', type=str, action='store', required=False)
    args = parser.parse_args()

    image_metadata = system_read_image_metadata(args.camera_id, args.format, args.start_ms, args.end_ms)
    requests.post(args.webhook, json={
        'response_type': 'in_channel',
        'blocks': [{
            'type': 'image',
            'image_url': data['bucket_url'],
            'alt_text': data['bucket_url'],
        } for data in image_metadata]
    })

if __name__ == '__main__':
    worker_main()