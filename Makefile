.PHONY: install-helm-redis
install-helm-redis:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install redis-helm bitnami/redis --set usePassword=false --set cluster.enabled=false  --set master.persistence.enabled=false  --namespace=default

.PHONY: black
black:
	black app/ -l 120

.PHONY: isort
isort:
	isort --recursive app/

.PHONY: fixstyle
fixstyle: black isort

.PHONY: lint-isort
lint-isort:
	isort --check-only --diff --recursive app/

.PHONY: lint-black
lint-black:
	black -l 120 --check --diff app/

.PHONY: lint
lint: lint-black lint-isort

.PHONY: test
test:
	cd app/ && python -m pytest tests/ -vv

.PHONY: fmt
fmt:
	black -l 120 app/
	isort --recursive app/
