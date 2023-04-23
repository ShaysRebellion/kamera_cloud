from fastapi import FastAPI
import logging
from .api import slack_api_v1
from .mqtt import init_app_mqtt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

app = FastAPI()
init_app_mqtt(app)
app.mount('/api/v1/slack', slack_api_v1)

@app.get('/')
def root():
    return { 'message': 'Hello World' }
