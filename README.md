# kamera_cloud
Introductory slides for this project can be found here: <https://docs.google.com/presentation/d/1VLYeOew4kmw3NbKI6OEDu_sAIKx5KwiUcabmvcyAHvM/edit?usp=sharing><br>

## Setup
### General
1. **重要**. Create AWS S3 bucket and IAM user along with IAM user access id and key credentials. Update credentials in the *kamera_cloud/vm-minikube-apps/webserver/deployment/secret.yaml* file. However, should the user decide to fork/branch this project, be careful not to push files with credentials...otherwise, the AWS team will hunt you down (笑)
2. The default AWS S3 bucket is *kamera-cloud-image-bucket*. However, users can set the AWS S3 bucket name by setting the environmental variable *AWS_S3_IMAGE_BUCKET* in *kamera_cloud/vm-minikube-apps/webserver/deployment/deployment.yaml*.
3. The default AWS S3 region is *ap-northeast-1* (東京). However, users can set the AWS S3 region by setting the environmental variable *AWS_S3_IMAGE_BUCKET_REGION* in *kamera_cloud/vm-minikube-apps/webserver/deployment/deployment.yaml*.

### Client
In *kamera_cloud/host-app*, run *app-init.sh*. This script assumes that *pyenv virtualenv* is installed on the system and creates a python 3.10.0 virtual environment called *kamera-cloud-client-3.10.0* that will activate whenever the user navigates into the *host-app* directory and also install any necessary python package dependencies. For more details, please refer to the documention within the script.

### Virtual machine
1. Create a virtual machine that shares a **192.168.205.2** interface. The easiest way to achieve this is to install *mulitpass* and run *multipass launch minikube --cpus 8 --memory 8G --mount $HOME/path_to_repo/kamera_cloud/vm-minikube-apps:/app*. On macOS, the user may need to modify entries in */var/db/dhcpd_leases*.
2. As mentioned in the previous step, mount the *kamera_cloud/vm-minikube-apps* directory to */app* within the virtual machine.
3. Shell into the virtual machine. With multipass: *multipass shell minikube*. Within the virtual machine, navigate to */app* and run *minikube-init.sh*. This script assumes that *minikube* is installed on the system and creates a minikube cluster with four nodes. Also please note that this script will take several minutes and depends on factors such as virtual machine resources (for intializing Kubernetes services) and network speed (for pulling docker images). For more details, please refer to the documentation within the script.

## Run
In *kamera_cloud/host-app*, run *python opencv-kamera.py*. Please note that if running on a computer with a webcam, then this webcam will be used. Since this package uses the *opencv_kamera* package, see <https://github.com/ShaysRebellion/opencv_kamera/blob/main/opencv_kamera/opencv_kamera/camera.py#L22>
