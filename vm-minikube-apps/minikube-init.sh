# Note: this script makes the following assumptions:
# 1. The machine is a Linux environment (host, VM, etc). Other environments such as macOS (and probably Windows) will not
#    properly resolve external cluster ip, i.e. minikube ip command.
# 2. minikube and kubectl are installed on this machine

# Initialize minikube cluster: the below are minimum resources required to run this application
minikube delete
minikube start --nodes 4 --cpus 2 --memory 2048 --driver docker

# https://github.com/kubernetes/minikube/issues/12360#issuecomment-1123794143)
minikube addons disable storage-provisioner
minikube addons disable default-storageclass
minikube addons enable volumesnapshots
minikube addons enable csi-hostpath-driver
kubectl patch storageclass csi-hostpath-sc -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
minikube addons enable ingress

# Set up postgres Kubernetes service:
cd /app/postgres
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f statefulset.yaml
kubectl apply -f service.yaml

# Set up rabbitmq cluster Kubernetes service:
cd /app/rabbitmq
kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"
kubectl apply -f namespace.yaml
kubectl apply -f rabbitmq.yaml
kubectl cp cluster-init.sh rabbitmq-cluster/rabbitmq-cluster-server-0:/tmp
kubectl exec -it rabbitmq-cluster-server-0 -n rabbitmq-cluster -- /bin/bash /tmp/cluster-init.sh

# Set up redis cluster Kubernetes service:
cd /app/redis-cluster
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f service.yaml
kubectl apply -f statefulset.yaml
kubectl cp cluster-init.sh redis-cluster/redis-cluster-0:/tmp
kubectl exec -it redis-cluster-0 -n redis-cluster -- /bin/bash /tmp/cluster-init.sh

# Set up webserver service:
cd /app/webserver/deployment
kubectl apply -f namespace.yaml
kubectl apply -f secret.yaml
kubectl apply -f ingress.yaml
kubectl apply -f service.yaml
kubectl apply -f deployment.yaml

if ! grep -q host-vm.io /etc/hosts; then
    echo -e "# For forwarding http traffic to (minikube) cluster" >> /etc/hosts
    echo -e "192.168.205.2 listen host-vm.io\n" >> /etc/hosts
fi

if ! grep -q minikube.io /etc/hosts; then
    echo -e "# For forwarding mqtt traffic to (minikube) cluster" >> /etc/hosts
    echo -e "192.168.49.2 minikube.io\n" >> /etc/hosts
fi

# Set up nginx proxy for forwarding mqtt and http traffic
cd /app
docker pull nginx:latest
docker run -d --rm --network host -v ./nginx.conf:/etc/nginx/nginx.conf --name nginx-kubernetes-proxy nginx:latest

echo "In a separate tab/window; please run: minikube tunnel. This enables mqtt traffic forwarding."
