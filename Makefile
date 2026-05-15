# SmartCharge AI - Development Makefile
# Simplifies common development tasks

.PHONY: help install setup start stop restart logs clean test lint format build deploy

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)SmartCharge AI - Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Installation and Setup
install: ## Install all dependencies (backend + frontend)
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@cd frontend && npm install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

setup: ## Initial project setup (copy env files, create dirs)
	@echo "$(BLUE)Setting up project...$(NC)"
	@cp -n backend/.env.example backend/.env 2>/dev/null || true
	@cp -n frontend/.env.example frontend/.env 2>/dev/null || true
	@mkdir -p logs ibm-bob-reports/decision-logs
	@echo "$(GREEN)✓ Project setup complete$(NC)"
	@echo "$(YELLOW)⚠ Remember to configure your .env files with IBM Bob credentials$(NC)"

# Docker Commands
start: ## Start all services with Docker Compose
	@echo "$(BLUE)Starting SmartCharge AI services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:5173$(NC)"
	@echo "$(YELLOW)Backend API: http://localhost:8000$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8000/docs$(NC)"

start-dev: ## Start only infrastructure (postgres, redis, simulator) for local development
	@echo "$(BLUE)Starting development infrastructure...$(NC)"
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Infrastructure started$(NC)"
	@echo "$(YELLOW)Run 'make run-backend' and 'make run-frontend' in separate terminals$(NC)"

stop: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	@docker-compose down
	@docker-compose -f docker-compose.dev.yml down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	@docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

logs: ## View logs from all services
	@docker-compose logs -f

logs-backend: ## View backend logs only
	@docker-compose logs -f backend

logs-frontend: ## View frontend logs only
	@docker-compose logs -f frontend

logs-simulator: ## View simulator logs only
	@docker-compose logs -f simulator

# Local Development
run-backend: ## Run backend locally (requires start-dev first)
	@echo "$(BLUE)Starting backend server...$(NC)"
	@cd backend && . venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Run frontend locally (requires start-dev first)
	@echo "$(BLUE)Starting frontend dev server...$(NC)"
	@cd frontend && npm run dev

run-simulator: ## Run simulator locally
	@echo "$(BLUE)Starting telemetry simulator...$(NC)"
	@cd simulator && python simulator.py

# Testing
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	@$(MAKE) test-backend
	@$(MAKE) test-frontend
	@echo "$(GREEN)✓ All tests passed$(NC)"

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	@cd backend && . venv/bin/activate && pytest --cov=app --cov-report=term-missing

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	@cd frontend && npm test -- --run

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	@cd backend && . venv/bin/activate && pytest tests/integration/ -v

# Code Quality
lint: ## Run linters on all code
	@echo "$(BLUE)Running linters...$(NC)"
	@$(MAKE) lint-backend
	@$(MAKE) lint-frontend
	@echo "$(GREEN)✓ Linting complete$(NC)"

lint-backend: ## Run backend linters (flake8, mypy)
	@echo "$(BLUE)Linting backend...$(NC)"
	@cd backend && . venv/bin/activate && flake8 . && mypy .

lint-frontend: ## Run frontend linter (eslint)
	@echo "$(BLUE)Linting frontend...$(NC)"
	@cd frontend && npm run lint

format: ## Format all code
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(MAKE) format-backend
	@$(MAKE) format-frontend
	@echo "$(GREEN)✓ Formatting complete$(NC)"

format-backend: ## Format backend code (black)
	@echo "$(BLUE)Formatting backend...$(NC)"
	@cd backend && . venv/bin/activate && black .

format-frontend: ## Format frontend code (prettier)
	@echo "$(BLUE)Formatting frontend...$(NC)"
	@cd frontend && npm run format

# Database
db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@cd backend && . venv/bin/activate && alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "$(RED)⚠ WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		sleep 5; \
		$(MAKE) db-migrate; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	fi

db-shell: ## Open PostgreSQL shell
	@docker exec -it smartcharge-postgres psql -U smartcharge -d smartcharge_db

db-backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(NC)"
	@docker exec smartcharge-postgres pg_dump -U smartcharge smartcharge_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backed up$(NC)"

# Build
build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker-compose build
	@echo "$(GREEN)✓ Build complete$(NC)"

build-backend: ## Build backend Docker image
	@echo "$(BLUE)Building backend image...$(NC)"
	@docker-compose build backend
	@echo "$(GREEN)✓ Backend image built$(NC)"

build-frontend: ## Build frontend Docker image
	@echo "$(BLUE)Building frontend image...$(NC)"
	@docker-compose build frontend
	@echo "$(GREEN)✓ Frontend image built$(NC)"

build-prod: ## Build production frontend bundle
	@echo "$(BLUE)Building production frontend...$(NC)"
	@cd frontend && npm run build
	@echo "$(GREEN)✓ Production build complete$(NC)"

# Cleanup
clean: ## Clean up temporary files and caches
	@echo "$(BLUE)Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@rm -rf backend/htmlcov frontend/coverage 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-docker: ## Remove all Docker containers, volumes, and images
	@echo "$(RED)⚠ WARNING: This will remove all Docker resources!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		echo "$(GREEN)✓ Docker cleanup complete$(NC)"; \
	fi

# Health Checks
health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo "Backend: $$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' || echo '$(RED)DOWN$(NC)')"
	@echo "Frontend: $$(curl -s http://localhost:5173 > /dev/null && echo '$(GREEN)UP$(NC)' || echo '$(RED)DOWN$(NC)')"
	@echo "PostgreSQL: $$(docker exec smartcharge-postgres pg_isready -U smartcharge > /dev/null 2>&1 && echo '$(GREEN)UP$(NC)' || echo '$(RED)DOWN$(NC)')"
	@echo "Redis: $$(docker exec smartcharge-redis redis-cli ping > /dev/null 2>&1 && echo '$(GREEN)UP$(NC)' || echo '$(RED)DOWN$(NC)')"

status: ## Show status of all services
	@docker-compose ps

# Documentation
docs: ## Generate API documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)API Docs available at: http://localhost:8000/docs$(NC)"
	@echo "$(YELLOW)ReDoc available at: http://localhost:8000/redoc$(NC)"

# Deployment
deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	@echo "$(YELLOW)⚠ Not implemented yet$(NC)"

deploy-prod: ## Deploy to production environment
	@echo "$(BLUE)Deploying to production...$(NC)"
	@echo "$(YELLOW)⚠ Not implemented yet$(NC)"

# Utilities
shell-backend: ## Open shell in backend container
	@docker exec -it smartcharge-backend /bin/bash

shell-frontend: ## Open shell in frontend container
	@docker exec -it smartcharge-frontend /bin/sh

shell-postgres: ## Open shell in postgres container
	@docker exec -it smartcharge-postgres /bin/bash

shell-redis: ## Open shell in redis container
	@docker exec -it smartcharge-redis /bin/sh

# Quick Start
quickstart: setup install start ## Complete quickstart (setup + install + start)
	@echo "$(GREEN)✓ SmartCharge AI is ready!$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:5173$(NC)"
	@echo "$(YELLOW)Backend API: http://localhost:8000/docs$(NC)"

# Made with Bob
