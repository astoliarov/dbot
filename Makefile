.PHONY: install-helm-redis
install-helm-redis:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install redis-helm bitnami/redis --set usePassword=false --set cluster.enabled=false  --set master.persistence.enabled=false  --namespace=default

.PHONY: lint-isort
lint-isort:
	isort --check-only --diff .

.PHONY: lint-black
lint-black:
	black -l 120 --check --diff .

.PHONY: lint
lint: lint-black lint-isort

.PHONY: test
test:
	cd app/ && python -m pytest tests/ -vv

.PHONY: fmt
fmt:
	black -l 120 ./app
	isort ./app

.PHONY: local-deploy/infrastructure
local-deploy/infrastructure:
	docker compose --profile=infra up

.PHONY: application/run-local
application/run-local:
	cd app/ && python ./main.py
