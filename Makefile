.PHONY: help setup backend frontend train clean

help:
	@echo "AI Prompt Firewall - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Complete setup (backend + frontend)"
	@echo "  make setup-backend  - Setup backend only"
	@echo "  make setup-frontend - Setup frontend only"
	@echo "  make train          - Train ML model"
	@echo ""
	@echo "Development:"
	@echo "  make backend        - Start backend server"
	@echo "  make frontend       - Start frontend server"
	@echo "  make dev            - Start both (requires 2 terminals or tmux)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove venv, node_modules, .env files"
	@echo ""

setup:
	bash setup.sh

setup-backend:
	cd backend && bash scripts/setup_backend.sh

setup-frontend:
	cd frontend && bash setup.sh

train:
	cd backend && bash scripts/train_model.sh

backend:
	cd backend && bash scripts/dev.sh

frontend:
	cd frontend && bash dev.sh

clean:
	rm -rf backend/venv backend/.env
	rm -rf frontend/node_modules frontend/.env.local
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete