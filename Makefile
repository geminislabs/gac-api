.PHONY: help install install-dev lint format format-check test test-cov build run run-dev stop clean deploy-test validate all-checks health logs shell db-shell migrations-create migrations-up migrations-down migrations-history dev

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Instala las dependencias de producción
	pip install -r requirements.txt

install-dev:  ## Instala dependencias de desarrollo
	pip install -r requirements-dev.txt
	pip install pytest-cov ruff black

lint:  ## Ejecuta el linter (Ruff)
	ruff check app/ tests/

format:  ## Formatea el código con Black
	black app/ tests/

format-check:  ## Verifica el formato sin modificar archivos
	black --check app/ tests/

test:  ## Ejecuta los tests
	pytest tests/ -v

test-cov:  ## Ejecuta los tests con coverage (umbrales en pyproject.toml / CI)
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

build:  ## Construye la imagen Docker
	docker build -t gac-api:latest .

run:  ## Ejecuta el contenedor localmente (producción)
	docker network create siscom-network 2>/dev/null || true
	docker-compose -f docker-compose.prod.yml up -d

run-dev:  ## Ejecuta en modo desarrollo con hot-reload (puerto 8000)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

stop:  ## Detiene los contenedores
	docker-compose -f docker-compose.prod.yml down

logs:  ## Muestra los logs del contenedor
	docker logs -f gac-api

clean:  ## Limpia archivos temporales y caché
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage

deploy-test:  ## Prueba el deployment localmente
	docker network create siscom-network 2>/dev/null || true
	docker-compose -f docker-compose.prod.yml up -d

deploy-test-logs:  ## Muestra los logs del deployment de prueba
	docker logs -f gac-api

deploy-test-stop:  ## Detiene el deployment de prueba
	docker-compose -f docker-compose.prod.yml down

health:  ## Verifica el health check
	@echo "Verificando health check..."
	@curl -f http://localhost:8000/health && echo "\n✅ Health check OK" || echo "\n❌ Health check FAILED"

shell:  ## Abre una shell en el contenedor
	docker exec -it gac-api /bin/bash

all-checks: format-check lint test  ## Ejecuta todas las verificaciones (formato, lint, tests)
	@echo "✅ Todas las verificaciones pasaron correctamente"

validate: format-check lint test build  ## Pipeline local equivalente a CI quality
	@echo "✅ validate OK"

migrations-create:  ## Crea una nueva migración (usar: make migrations-create NAME="nombre")
	alembic revision --autogenerate -m "$(NAME)"

migrations-up:  ## Aplica todas las migraciones pendientes
	alembic upgrade head

migrations-down:  ## Revierte la última migración
	alembic downgrade -1

migrations-history:  ## Muestra el historial de migraciones
	alembic history

test-db-up:  ## Levanta PostgreSQL de test (docker-compose.test.yml)
	docker compose -f docker-compose.test.yml up -d

test-db-down:  ## Detiene PostgreSQL de test
	docker compose -f docker-compose.test.yml down

dev: run-dev  ## Alias de run-dev
