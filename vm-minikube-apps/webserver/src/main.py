from fastapi import FastAPI
import logging
from .slackapi import slack_api_v1
from .mqtt import init_app_mqtt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, force=True)
log = logging.getLogger(__name__)

app = FastAPI()
init_app_mqtt(app)
app.mount('/api/v1/slack', slack_api_v1)

@app.get('/')
def root():
    return { 'message': 'Hello World' }
