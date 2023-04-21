from fastapi import FastAPI
from .api import appv1
from .mqtt import init_app_mqtt

app = FastAPI()
init_app_mqtt(app)
app.mount('/api/v1', appv1)

@app.get('/')
def root():
    return { 'message': 'Hello World' }
