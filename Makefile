POETRY ?= poetry
LINT_SOURCES_DIRS = src tests

###########################
# Environment configuration
###########################

.PHONY: poetry/install
poetry/install:
	pip install poetry==1.6.1

.PHONY: poetry
poetry: poetry/install

.PHONY: install
install:
	$(POETRY) install --without dev

.PHONY: install-dev
install-dev:
	$(POETRY) install

.PHONY: env/prepare
env/prepare:
	cp .env.example .env
	cp .envrc.example .envrc

##################
# Code style tools
##################

.PHONY: lint/black
lint/black:
	@echo "\033[92m< linting using black...\033[0m"
	$(POETRY) run black --check --diff $(LINT_SOURCES_DIRS)
	@echo "\033[92m> done\033[0m"
	@echo


.PHONY: lint/isort
lint/isort:
	@echo "\033[92m< linting using isort...\033[0m"
	$(POETRY) run isort --check-only --diff $(LINT_SOURCES_DIRS)
	@echo "\033[92m> done\033[0m"
	@echo

.PHONY: lint/mypy
lint/mypy:
	@echo "\033[92m< linting using mypy...\033[0m"
	$(POETRY) run mypy --show-error-codes --skip-cache-mtime-checks $(LINT_SOURCES_DIRS)
	@echo "\033[92m> done\033[0m"
	@echo

.PHONY: lint
lint: lint/black lint/isort lint/mypy


.PHONY: fmt/black
fmt/black:
	@echo "\033[92m< formatting using black...\033[0m"
	$(POETRY) run black $(LINT_SOURCES_DIRS)
	@echo "\033[92m> done\033[0m"
	@echo

.PHONY: fmt/isort
fmt/isort:
	@echo "\033[92m< formatting using isort...\033[0m"
	$(POETRY) run isort $(LINT_SOURCES_DIRS)
	@echo "\033[92m> done\033[0m"
	@echo

.PHONY: fmt
fmt: fmt/black fmt/isort

#########
# Testing
#########

.PHONY: test/unit
test/unit: TESTS ?= tests/unit
test/unit:
	$(POETRY) run python -m pytest -vv $(TESTS)

.PHONY: test/integration
test/integration: TESTS ?= tests/integration
test/integration:
	$(POETRY) run python -m pytest -vv $(TESTS)

.PHONY: test
test: test/unit test/integration

#############
# Entrypoints
#############

.PHONY: local-deploy/infrastructure/up
local-deploy/infrastructure/up:
	docker compose --profile=infra up

.PHONY: local-deploy/infrastructure/down
local-deploy/infrastructure/down:
	docker compose --profile=infra down

.PHONY: local-deploy/application
local-deploy/application:
	docker compose --profile=infra --profile=app up --build

.PHONY: run/app
run/app:
	python src/dbot/main.py

##########
### Docker
##########

IMAGE ?=dbot
TAG ?= latest

.PHONY: docker/build
docker/build:
	docker build . \
	--tag $(IMAGE):latest \
	--target base \
	--file ./Dockerfile

.PHONY: docker/tag
docker/tag:
	docker tag $(IMAGE):latest $(IMAGE):$(TAG)

