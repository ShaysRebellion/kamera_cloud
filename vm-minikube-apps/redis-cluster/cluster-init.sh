redis-cli --cluster create --cluster-replicas 1 \
  $(getent hosts redis-cluster-0.redis-cluster.redis-cluster.svc.cluster.local | awk '{ print $1 }'):6379 \
  $(getent hosts redis-cluster-1.redis-cluster.redis-cluster.svc.cluster.local | awk '{ print $1 }'):6379 \
  $(getent hosts redis-cluster-2.redis-cluster.redis-cluster.svc.cluster.local | awk '{ print $1 }'):6379 \
  $(getent hosts redis-cluster-3.redis-cluster.redis-cluster.svc.cluster.local | awk '{ print $1 }'):6379 \
  $(getent hosts redis-cluster-4.redis-cluster.redis-cluster.svc.cluster.local | awk '{ print $1 }'):6379 \
  $(getent hosts redis-cluster-5.redis-cluster.redis-cluster.svc.cluster.local | awk '{ print $1 }'):6379
