# Async Agent System - Development Makefile
# Provides convenient commands for development workflow

.PHONY: help install build test lint format clean run dev setup check all

# Default target
help: ## Show this help message
	@echo "Async Agent System - Development Commands"
	@echo "========================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make setup     # Initial project setup"
	@echo "  make dev       # Start development servers"
	@echo "  make test      # Run all tests"
	@echo "  make build     # Build all components"

# =============================================================================
# Setup and Installation
# =============================================================================

setup: ## Complete project setup (install dependencies, setup environment)
	@echo "🚀 Setting up Async Agent System..."
	@$(MAKE) install-server
	@$(MAKE) install-ui
	@$(MAKE) setup-git-hooks
	@echo "✅ Setup complete!"

install: setup ## Alias for setup

install-server: ## Install Python server dependencies
	@echo "📦 Installing Python server dependencies..."
	cd packages/server && uv venv .venv
	cd packages/server && source .venv/bin/activate && uv sync
	cd packages/server && source .venv/bin/activate && pre-commit install

install-ui: ## Install Rust UI dependencies
	@echo "🦀 Installing Rust UI dependencies..."
	cd packages/ui && cargo fetch

setup-git-hooks: ## Setup git hooks for code quality
	@echo "🔧 Setting up git hooks..."
	cd packages/server && pre-commit install || echo "Pre-commit already installed"

# =============================================================================
# Development
# =============================================================================

dev: ## Start development servers (server + UI)
	@echo "🔥 Starting development servers..."
	@$(MAKE) -j2 dev-server dev-ui

dev-server: ## Start Python server in development mode
	@echo "🐍 Starting Python server..."
	cd packages/server && source .venv/bin/activate && uvicorn src.server:app --reload --port 8000

dev-ui: ## Start Rust UI in development mode
	@echo "🦀 Starting Rust UI..."
	cd packages/ui && cargo run

run: dev ## Alias for dev

run-server: dev-server ## Alias for dev-server

run-ui: dev-ui ## Alias for dev-ui

# =============================================================================
# Building
# =============================================================================

build: ## Build all components
	@echo "🔨 Building all components..."
	@$(MAKE) build-server
	@$(MAKE) build-ui
	@echo "✅ Build complete!"

build-server: ## Build Python server
	@echo "🐍 Building Python server..."
	cd packages/server && source .venv/bin/activate && python -m py_compile src/*.py

build-ui: ## Build Rust UI
	@echo "🦀 Building Rust UI..."
	cd packages/ui && cargo build

build-release: ## Build optimized release versions
	@echo "🚀 Building release versions..."
	cd packages/ui && cargo build --release
	@echo "✅ Release build complete!"

# =============================================================================
# Testing
# =============================================================================

test: ## Run all tests
	@echo "🧪 Running all tests..."
	@$(MAKE) test-server
	@$(MAKE) test-ui
	@echo "✅ All tests passed!"

test-server: ## Run Python server tests
	@echo "🐍 Running Python server tests..."
	cd packages/server && source .venv/bin/activate && python -m pytest

test-ui: ## Run Rust UI tests
	@echo "🦀 Running Rust UI tests..."
	cd packages/ui && cargo test

test-watch: ## Run tests in watch mode
	@echo "👀 Running tests in watch mode..."
	cd packages/ui && cargo watch -x test

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run linters on all code
	@echo "🔍 Running linters..."
	@$(MAKE) lint-server
	@$(MAKE) lint-ui
	@echo "✅ Linting complete!"

lint-server: ## Run Python linters
	@echo "🐍 Linting Python code..."
	cd packages/server && source .venv/bin/activate && uv run ruff check . --fix
	cd packages/server && source .venv/bin/activate && uv run ruff format .

lint-ui: ## Run Rust linters
	@echo "🦀 Linting Rust code..."
	cd packages/ui && cargo clippy -- -D warnings
	cd packages/ui && cargo fmt

format: ## Format all code
	@echo "✨ Formatting code..."
	@$(MAKE) format-server
	@$(MAKE) format-ui
	@echo "✅ Formatting complete!"

format-server: ## Format Python code
	@echo "🐍 Formatting Python code..."
	cd packages/server && source .venv/bin/activate && uv run ruff format .

format-ui: ## Format Rust code
	@echo "🦀 Formatting Rust code..."
	cd packages/ui && cargo fmt

check: ## Check code quality without fixing
	@echo "🔍 Checking code quality..."
	@$(MAKE) check-server
	@$(MAKE) check-ui
	@echo "✅ Code quality check complete!"

check-server: ## Check Python code quality
	@echo "🐍 Checking Python code..."
	cd packages/server && source .venv/bin/activate && uv run ruff check .
	cd packages/server && source .venv/bin/activate && python -m py_compile src/*.py

check-ui: ## Check Rust code quality
	@echo "🦀 Checking Rust code..."
	cd packages/ui && cargo check
	cd packages/ui && cargo clippy -- -D warnings

# =============================================================================
# Database and Services
# =============================================================================

db-up: ## Start database services (if using Docker)
	@echo "🗄️ Starting database services..."
	@if [ -f docker-compose.yml ]; then \
		docker-compose up -d; \
	else \
		echo "No docker-compose.yml found"; \
	fi

db-down: ## Stop database services
	@echo "🛑 Stopping database services..."
	@if [ -f docker-compose.yml ]; then \
		docker-compose down; \
	else \
		echo "No docker-compose.yml found"; \
	fi

db-reset: ## Reset database
	@echo "🔄 Resetting database..."
	@$(MAKE) db-down
	@$(MAKE) db-up

# =============================================================================
# Deployment
# =============================================================================

deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	@$(MAKE) build-release
	@echo "⚠️  Staging deployment not configured yet"

deploy-prod: ## Deploy to production environment
	@echo "🚀 Deploying to production..."
	@$(MAKE) build-release
	@echo "⚠️  Production deployment not configured yet"

# =============================================================================
# Maintenance
# =============================================================================

clean: ## Clean build artifacts and caches
	@echo "🧹 Cleaning build artifacts..."
	@$(MAKE) clean-server
	@$(MAKE) clean-ui
	@echo "✅ Clean complete!"

clean-server: ## Clean Python artifacts
	@echo "🐍 Cleaning Python artifacts..."
	cd packages/server && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd packages/server && find . -name "*.pyc" -delete 2>/dev/null || true
	cd packages/server && rm -rf .pytest_cache 2>/dev/null || true

clean-ui: ## Clean Rust artifacts
	@echo "🦀 Cleaning Rust artifacts..."
	cd packages/ui && cargo clean

update: ## Update dependencies
	@echo "📦 Updating dependencies..."
	@$(MAKE) update-server
	@$(MAKE) update-ui
	@echo "✅ Dependencies updated!"

update-server: ## Update Python dependencies
	@echo "🐍 Updating Python dependencies..."
	cd packages/server && source .venv/bin/activate && uv sync --upgrade

update-ui: ## Update Rust dependencies
	@echo "🦀 Updating Rust dependencies..."
	cd packages/ui && cargo update

# =============================================================================
# Documentation
# =============================================================================

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@$(MAKE) docs-ui
	@echo "✅ Documentation generated!"

docs-ui: ## Generate Rust documentation
	@echo "🦀 Generating Rust documentation..."
	cd packages/ui && cargo doc --open

# =============================================================================
# Utilities
# =============================================================================

logs: ## Show application logs
	@echo "📋 Showing logs..."
	@if [ -f docker-compose.yml ]; then \
		docker-compose logs -f; \
	else \
		echo "No docker-compose.yml found for logs"; \
	fi

ps: ## Show running processes
	@echo "📊 Showing running processes..."
	@ps aux | grep -E "(uvicorn|cargo|async)" | grep -v grep || echo "No async processes running"

env: ## Show environment information
	@echo "🌍 Environment Information"
	@echo "========================="
	@echo "Python version: $$(python3 --version 2>/dev/null || echo 'Not found')"
	@echo "Rust version: $$(rustc --version 2>/dev/null || echo 'Not found')"
	@echo "UV version: $$(uv --version 2>/dev/null || echo 'Not found')"
	@echo "Cargo version: $$(cargo --version 2>/dev/null || echo 'Not found')"
	@echo "Git version: $$(git --version 2>/dev/null || echo 'Not found')"
	@echo "Docker version: $$(docker --version 2>/dev/null || echo 'Not found')"

# =============================================================================
# CI/CD Simulation
# =============================================================================

ci: ## Run CI pipeline locally
	@echo "🔄 Running CI pipeline..."
	@$(MAKE) check
	@$(MAKE) test
	@$(MAKE) build
	@echo "✅ CI pipeline completed successfully!"

all: ci ## Run complete CI pipeline

# =============================================================================
# Quick Development Workflows
# =============================================================================

quick-start: ## Quick start for new developers
	@echo "⚡ Quick start for development..."
	@$(MAKE) setup
	@$(MAKE) check
	@echo "🎉 Ready to develop! Run 'make dev' to start servers"

reset: ## Reset development environment
	@echo "🔄 Resetting development environment..."
	@$(MAKE) clean
	@$(MAKE) setup
	@echo "✅ Environment reset complete!"

# =============================================================================
# Git Helpers
# =============================================================================

git-hooks: setup-git-hooks ## Setup git hooks

pre-commit: ## Run pre-commit checks
	@echo "🔍 Running pre-commit checks..."
	cd packages/server && source .venv/bin/activate && pre-commit run --all-files

# =============================================================================
# Development Status
# =============================================================================

status: ## Show development status
	@echo "📊 Development Status"
	@echo "===================="
	@echo ""
	@echo "🐍 Python Server:"
	@echo "  Dependencies: $$(cd packages/server && source .venv/bin/activate && pip list | wc -l) packages installed"
	@echo "  Tests: $$(cd packages/server && find . -name '*test*.py' | wc -l) test files"
	@echo ""
	@echo "🦀 Rust UI:"
	@echo "  Dependencies: $$(cd packages/ui && cargo tree --depth 1 | wc -l) crates"
	@echo "  Source files: $$(find packages/ui/src -name '*.rs' | wc -l) Rust files"
	@echo ""
	@echo "📁 Project Structure:"
	@echo "  Total files: $$(find . -type f | wc -l)"
	@echo "  Code files: $$(find . -name '*.py' -o -name '*.rs' | wc -l)"
	@echo ""
	@echo "Run 'make help' for available commands"
