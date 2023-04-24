from datetime import datetime
import logging
# from os.path import dirname, abspath
import re
# import subprocess
from fastapi import FastAPI, Request
from .operations import system_read_image_metadata

log = logging.getLogger(__name__)

# worker_file = '{dir}/worker.py'.format(dir = dirname(dirname(abspath(__file__))))
slack_api_v1 = FastAPI()

HELP_REGEX = re.compile(r'help')
CAMERA_ID_REGEX = re.compile(r'cameraId=[0-9]+')
FORMAT_REGEX = re.compile(r'format=\.[a-zA-Z]+')
START_REGEX = re.compile(r'start=[0-9]+\.[0-9]+\.[0-9]+::[0-9]+:[0-9]+:[0-9]+')
END_REGEX = re.compile(r'end=[0-9]+\.[0-9]+\.[0-9]+::[0-9]+:[0-9]+:[0-9]+')

@slack_api_v1.post('/images')
def financial_data(request: Request):
    command_args = request.query_params['text']
    # webhook = request.query_params['response_url']

    help_match = HELP_REGEX.search(command_args)
    if help_match:
        return {
            'response_type': 'ephemeral',
            'text': 'Sample usage: /images cameraId=0 (optional) format=.jpg (optional) start=08.08.2008::08.08.08 end=09.09.2009::09.09.09',
        }

    camera_match = CAMERA_ID_REGEX.search(command_args)
    format_match = FORMAT_REGEX.search(command_args)
    start_match = START_REGEX.search(command_args)
    end_match = END_REGEX.search(command_args)

    camera_id = ''
    format = ''
    timestamp_start_ms = 0
    timestamp_end_ms = 0

    if camera_match: camera_id = camera_match.string.split('=')[1]
    if format_match: format = format_match.string.split('=')[1]

    if not start_match:
        return {
            'response_type': 'ephemeral',
            'text': 'Missing start time argument (see help for sample usage)',
        }
    else:
        try:
            datetime_start = datetime.strptime('%d.%m.%Y::%H:%M:%S', start_match.string.split('=')[1])
            timestamp_start_ms = round(datetime_start.timestamp() * 1000)
        except Exception as e:
            log.info(e)
            return {
                'response_type': 'ephemeral',
                'text': 'Invalid start time argument: {arg} (see help for sample usage)'.format(start_match.string),
            }

    if not end_match:
        return {
            'response_type': 'ephemeral',
            'text': 'Missing end time argument (see help for sample usage)',
        }
    else:
        try:
            datetime_end = datetime.strptime('%d.%m.%Y::%H:%M:%S', end_match.string.split('=')[1])
            timestamp_end_ms = round(datetime_end.timestamp() * 1000)
        except Exception as e:
            log.info(e)
            return {
                'response_type': 'ephemeral',
                'text': 'Invalid end time argument: {arg} (see help for sample usage)'.format(end_match.string),
            }

    image_metadata = system_read_image_metadata(int(camera_id), format, timestamp_start_ms, timestamp_end_ms)

    return {
        'response_type': 'in_channel',
        'blocks': [{
            'type': 'image',
            'image_url': data['bucket_url'],
            'alt_text': data['bucket_url'],
        } for data in image_metadata]
    }

    # command = ['python', worker_file, '--webhook', webhook, '--startMs', str(timestamp_start_ms), '--endMs', str(timestamp_end_ms)]
    # if camera_id: command.extend(['--cameraId', camera_id])
    # if format: command.extend(['--format', format])
    # subprocess.Popen(command)

    # return {
    #     'response_type': 'ephemeral',
    #     'text': 'Parsed arguments. \
    #         Camera ID: {camera_id}. \
    #         Format: {format}. \
    #         Start timestamp (ms): {timestamp_start_ms}. \
    #         End timestamp (ms): {timestamp_end_ms}.' \
    #         .format(
    #             camera_id = camera_id,
    #             format = format,
    #             timestamp_start_ms = timestamp_start_ms,
    #             timestamp_end_ms = timestamp_end_ms
    #         )
    # }
