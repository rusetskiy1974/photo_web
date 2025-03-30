DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
APP_FILE = docker/app.yaml
STORAGES_FILE = docker/storages.yaml
APP_CONTAINER = photo_web

export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

.PHONY: app
app:
	${DC} -f ${APP_FILE} ${ENV} up --build -d

.PHONY: storages
storages:
	${DC} -f ${STORAGES_FILE} ${ENV} up --build -d

.PHONY: all
all:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} ${ENV} up --build -d

.PHONY: app-down
app-down:
	${DC} -f ${APP_FILE} down

.PHONY: storages-down
storages-down:
	${DC} -f ${STORAGES_FILE} down

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} bash

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: test
test:
	${EXEC} ${APP_CONTAINER} pytest -m unit && pytest -m integration && pytest -m e2e

.PHONY: test-e2e
test-e2e:
	${EXEC} ${APP_CONTAINER} pytest -m e2e

.PHONY: test-unit
test-unit:
	${EXEC} ${APP_CONTAINER} pytest -m unit

.PHONY: test-int
test-int:
	${EXEC} ${APP_CONTAINER} pytest -m integration

.PHONY: migrate
migrate:
	${EXEC} ${APP_CONTAINER} alembic upgrade head

.PHONY: migrations
migrations:
	${EXEC} ${APP_CONTAINER} alembic revision -m "$(msg)" --autogenerate

.PHONY: downgrade
downgrade:
	${EXEC} ${APP_CONTAINER} alembic downgrade "$(rev)"

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make app              - Start the application with Docker Compose."
	@echo "  make storages         - Start storages (e.g., database, cache) with Docker Compose."
	@echo "  make all              - Start both the app and storages."
	@echo "  make app-down         - Stop the application."
	@echo "  make storages-down    - Stop the storages."
	@echo "  make app-shell        - Open a shell inside the application container."
	@echo "  make app-logs         - Show logs of the application container."
	@echo "  make test             - Run all tests (unit, integration, e2e)."
	@echo "  make test-unit        - Run unit tests."
	@echo "  make test-int         - Run integration tests."
	@echo "  make test-e2e         - Run end-to-end tests."
	@echo "  make migrate          - Apply all migrations using Alembic."
	@echo "  make migrations       - Create a new Alembic migration with a message."
	@echo "  make downgrade        - Downgrade the database to a specific revision."