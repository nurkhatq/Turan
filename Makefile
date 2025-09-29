.PHONY: help install dev-install test lint format clean docker-build docker-up docker-down migrate init-db create-admin structure

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

migrate: ## Run database migrations (use this instead of scripts/migrate.py)
	alembic upgrade head

setup-db: ## Complete database setup
	python scripts/setup_database.py

docker-build: ## Build Docker images
	docker-compose -f docker/docker-compose.yml build

test: ## Run tests
	pytest tests/ -v --cov=app --cov-report=html

docker-up: ## Start development environment
	docker-compose -f docker/docker-compose.yml up -d

docker-down: ## Stop development environment
	docker-compose -f docker/docker-compose.yml down

docker-logs: ## View Docker logs
	docker-compose -f docker/docker-compose.yml logs -f

setup: structure docker-up setup-db ## Complete setup for development

quick-fix: ## Quick fix for common issues
	make docker-build
	make docker-up
	sleep 10
	make setup-db