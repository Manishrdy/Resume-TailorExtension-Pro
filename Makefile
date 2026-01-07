.PHONY: help install dev prod test clean logs

help:  ## Show this help message
	@echo "Resume Tailor - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install Python dependencies locally
	cd backend && pip install -r requirements.txt

dev:  ## Start services in development mode
	docker-compose -f docker-compose.dev.yml up --build

dev-detached:  ## Start services in background
	docker-compose -f docker-compose.dev.yml up -d --build

prod:  ## Start services in production mode
	docker-compose up -d --build

stop:  ## Stop all services
	docker-compose -f docker-compose.dev.yml down
	docker-compose down

logs:  ## View logs from all services
	docker-compose -f docker-compose.dev.yml logs -f

logs-api:  ## View FastAPI logs only
	docker-compose -f docker-compose.dev.yml logs -f fastapi-dev

logs-pdf:  ## View Open Resume logs only
	docker-compose -f docker-compose.dev.yml logs -f open-resume-dev

test:  ## Run all tests
	cd backend && pytest

test-coverage:  ## Run tests with coverage report
	cd backend && pytest --cov=app --cov=models --cov=utils --cov-report=html --cov-report=term

test-unit:  ## Run unit tests only
	cd backend && pytest -m unit

health:  ## Check API health
	@curl -s http://localhost:8000/api/health | python -m json.tool

clean:  ## Clean up containers and volumes
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage backend/.pytest_cache

rebuild:  ## Rebuild and restart services
	docker-compose -f docker-compose.dev.yml down
	docker-compose -f docker-compose.dev.yml up --build

shell-api:  ## Open shell in FastAPI container
	docker-compose -f docker-compose.dev.yml exec fastapi-dev /bin/bash

shell-pdf:  ## Open shell in Open Resume container
	docker-compose -f docker-compose.dev.yml exec open-resume-dev /bin/sh

setup:  ## Initial project setup
	@echo "Setting up Resume Tailor..."
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "✓ Created backend/.env (remember to add your GEMINI_API_KEY)"; \
	fi
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Add your GEMINI_API_KEY to backend/.env"
	@echo "  2. Clone Open Resume repo: cd open-resume-service && git clone https://github.com/Manishrdy/open-resume.git ."
	@echo "  3. Run: make dev"
