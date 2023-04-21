minikube start --nodes 4 --cpus 2 --memory 2048 --driver docker

# https://github.com/kubernetes/minikube/issues/12360#issuecomment-1123794143)
minikube addons disable storage-provisioner
minikube addons disable default-storageclass
minikube addons enable volumesnapshots
minikube addons enable csi-hostpath-driver
kubectl patch storageclass csi-hostpath-sc -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
minikube addons enable ingress

while true; do
    read -p "Do you wish to install this program? " yn
    case $yn in
        [Yy]* ) make install; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# TODO: BREAKPOINT
minikube tunnel

# Postgres (postgres directory):
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f statefulset.yaml
kubectl apply -f service.yaml

# RabbitMq (rabbitmq directory):
kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"
kubectl apply -f namespace.yaml
kubectl apply -f rabbitmq.yaml

# Redis (redis directory)
kubectl apply -f redis-cluster-namespace.yaml
kubectl apply -f redis-cluster-service.yaml
kubectl apply -f redis-cluster.yaml
kubectl exec -it redis-cluster -n redis-cluster –- /bin/bash
copy and run redis-cluster-create.sh

docker pull nginx_kubernetes_proxy nginx:latest
docker run -d --rm --network host -v ./nginx.conf:/etc/nginx/nginx.conf --name nginx_kubernetes_proxy nginx:latest

# Insert into /etc/hosts for local dns resolution:
# For forwarding/connecting to rabbitmq broker within multipass virtual machine minikube
192.168.205.2 mqtt.kamera-cloud-rabbitmq.io
