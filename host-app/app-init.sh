# Note: this script makes the following assumptions:
# 1. pyenv virtual env is installed: https://github.com/pyenv/pyenv-virtualenv
# 2. rabbitmq broker hosted by (multipass) virtual machine can be reached at 192.168.205.2

pyenv install 3.10.0
pyenv virtualenv 3.10.0 kamera-cloud-client-3.10.0
pyenv local kamera-cloud-client-3.10.0
pip install -r requirements.txt

if ! grep -q mqtt.kamera-cloud-rabbitmq.io /etc/hosts; then
    echo "# For forwarding/connecting to rabbitmq broker within multipass virtual machine minikube" >> /etc/hosts
    echo "192.168.205.2 mqtt.kamera-cloud-rabbitmq.io" >> /etc/hosts
fi
