import subprocess

# for some reason will not automatically resolve to IP address, so manually input IP
def get_cluster_ip_address(hostname: str) -> str:
    cmd =  "getent hosts " + hostname + " | awk '{ print $1 }'"
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode()[0: -1]
