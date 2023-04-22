from datetime import datetime
import logging
from os.path import dirname, abspath
import re
import time
import subprocess
from typing import Tuple
from fastapi import FastAPI, Request

log = logging.getLogger(__name__)
worker_file = '{dir}/worker.py'.format(dir = dirname(dirname(abspath(__file__))))
slack_api_v1 = FastAPI()

CAMERA_ID_REGEX = re.compile(r'cameraId=[0-9]+')
FORMAT_REGEX = re.compile(r'format=\.[a-zA-Z]+')
START_REGEX = re.compile(r'start=[0-9]+\.[0-9]+\.[0-9]+::[0-9]+:[0-9]+:[0-9]+')
END_REGEX = re.compile(r'end=[0-9]+\.[0-9]+\.[0-9]+::[0-9]+:[0-9]+:[0-9]+')

def process_timestamps(timestamp_ms_lower: int = 0, timestamp_ms_upper: int = 0) -> Tuple[int, int]:
    if timestamp_ms_upper and timestamp_ms_lower and timestamp_ms_lower > timestamp_ms_upper:
        temp = timestamp_ms_lower
        timestamp_ms_lower = timestamp_ms_upper
        timestamp_ms_upper = temp
    elif not timestamp_ms_upper and not timestamp_ms_lower:
        timestamp_ms_upper = round(time.time() * 1000)
        timestamp_ms_lower = timestamp_ms_upper - (60 * 1000)  
    elif not timestamp_ms_upper and timestamp_ms_lower:
        timestamp_ms_upper = timestamp_ms_lower + (60 * 1000)
    elif timestamp_ms_upper and not timestamp_ms_lower:
        timestamp_ms_lower = timestamp_ms_upper - (60 * 1000)

    return timestamp_ms_lower, timestamp_ms_upper

@slack_api_v1.post('/images')
def financial_data(request: Request):
    command_args = request.query_params['text']
    webhook = request.query_params['response_url']

    camera_match = CAMERA_ID_REGEX.match(command_args)
    format_match = FORMAT_REGEX.match(command_args)
    start_match = START_REGEX.match(command_args)
    end_match = END_REGEX.match(command_args)

    camera_id = ''
    format = ''
    timestamp_start_ms = 0
    timestamp_end_ms = 0

    if camera_match: camera_id = camera_match.string.split('=')[1]
    if format_match: format = format_match.string.split('=')[1]
    
    if start_match:
        try:
            datetime_start = datetime.strptime('%d.%m.%Y::%H:%M:%S', start_match.string.split('=')[1])
            timestamp_start_ms = round(datetime_start.timestamp() * 1000)
        except Exception as e:
            log.debug(e)

    if end_match:
        try:
            datetime_end = datetime.strptime('%d.%m.%Y::%H:%M:%S', end_match.string.split('=')[1])
            timestamp_end_ms = round(datetime_end.timestamp() * 1000)
        except Exception as e:
            log.debug(e)

    timestamp_start_ms, timestamp_end_ms = process_timestamps(timestamp_start_ms, timestamp_end_ms)

    command = ['python', worker_file, '--webhook', webhook, '--startMs', str(timestamp_start_ms), '--endMs', str(timestamp_end_ms)]
    if camera_id: command.extend(['--cameraId', camera_id])
    if format: command.extend(['--format', format])
    subprocess.Popen(command)

    return {
        'response_type': 'ephemeral',
        'text': 'Parsed arguments. \
            Camera ID: {camera_id}. \
            Format: {format}. \
            Start timestamp (ms): {timestamp_start_ms}. \
            End timestamp (ms): {timestamp_end_ms}.' \
            .format(
                camera_id = camera_id,
                format = format,
                timestamp_start_ms = timestamp_start_ms,
                timestamp_end_ms = timestamp_end_ms
            )
    }
