install-helm-redis:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install redis-helm bitnami/redis --set usePassword=false --set cluster.enabled=false  --set master.persistence.enabled=false  --namespace=default

