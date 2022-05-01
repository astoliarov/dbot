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
	cd app/ && poetry run isort --check-only --diff .

.PHONY: lint-black
lint-black:
	cd app/ && poetry run black -l 120 --check --diff .

.PHONY: lint
lint: lint-black lint-isort

.PHONY: test
test:
	cd app/ && poetry run python -m pytest tests/ -vv

.PHONY: fmt
fmt:
	cd app/ && poetry run black -l 120 .
	cd app/ && poetry run isort .
