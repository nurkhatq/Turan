# Makefile
.PHONY: help install dev-install test lint format clean docker-build docker-up docker-down migrate init-db create-admin

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

test: ## Run tests
	pytest tests/ -v --cov=app --cov-report=html

lint: ## Run linting
	flake8 app/
	mypy app/

format: ## Format code
	black app/
	isort app/

clean: ## Clean cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

docker-build: ## Build Docker images
	docker-compose -f docker/docker-compose.yml build

docker-up: ## Start development environment
	docker-compose -f docker/docker-compose.yml up -d

docker-down: ## Stop development environment
	docker-compose -f docker/docker-compose.yml down

docker-prod-up: ## Start production environment
	docker-compose -f docker/docker-compose.prod.yml up -d

docker-logs: ## View Docker logs
	docker-compose -f docker/docker-compose.yml logs -f

migrate: ## Run database migrations
	python scripts/migrate.py

init-db: ## Initialize database
	python scripts/init_db.py

create-admin: ## Create admin user
	python scripts/create_admin.py

setup: docker-up migrate init-db create-admin ## Complete setup for development

prod-setup: docker-prod-up migrate init-db create-admin ## Complete setup for production