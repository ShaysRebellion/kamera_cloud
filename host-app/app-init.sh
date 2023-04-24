# Note: this script makes the following assumptions:
# 1. pyenv virtual env is installed: https://github.com/pyenv/pyenv-virtualenv
# 2. rabbitmq broker hosted by (multipass) virtual machine can be reached at 192.168.205.2

pyenv install 3.10.0
pyenv virtualenv 3.10.0 kamera-cloud-client-3.10.0
pyenv local kamera-cloud-client-3.10.0
pip install -r requirements.txt

if ! grep -q mqtt.kamera-cloud-rabbitmq.io /etc/hosts; then
    echo -e "# For connecting to rabbitmq broker within (multipass) virtual machine (minikube) Kubernertes cluster" >> /etc/hosts
    echo -e "192.168.205.2 mqtt.kamera-cloud-rabbitmq.io\n" >> /etc/hosts
fi

if ! grep -q host-vm.io /etc/hosts; then
    echo -e "# For connecting to Slack API backend within (multipass) virtual machine (minikube) Kubernertes cluster" >> /etc/hosts
    echo -e "192.168.205.2 kamera-cloud.io\n" >> /etc/hosts
fi
