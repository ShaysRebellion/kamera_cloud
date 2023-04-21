FROM python:3.10.0-bullseye

COPY ./requirements.txt /build/requirements.txt
RUN pip install -r /build/requirements.txt

COPY ./src /app
WORKDIR /
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
