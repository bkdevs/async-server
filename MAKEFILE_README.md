# Makefile Documentation

This document provides comprehensive documentation for the Async Agent System development Makefile, which streamlines the development workflow for this multi-language project.

## Overview

The Makefile provides convenient commands for managing a hybrid Python/Rust project with the following structure:
- **Server**: Python-based backend using FastAPI and UV for dependency management
- **UI**: Rust-based frontend using Cargo for build management

## Quick Start

```bash
# Complete project setup
make setup

# Start development servers
make dev

# Run all tests
make test

# Build all components
make build
```

## Command Categories

### 🚀 Setup and Installation

| Command | Description |
|---------|-------------|
| `make setup` | Complete project setup (install dependencies, setup environment) |
| `make install` | Alias for setup |
| `make install-server` | Install Python server dependencies using UV |
| `make install-ui` | Install Rust UI dependencies using Cargo |
| `make setup-git-hooks` | Setup pre-commit hooks for code quality |

**Example workflow for new developers:**
```bash
make setup          # One-time setup
make quick-start     # Alternative quick setup with checks
```

### 🔥 Development

| Command | Description |
|---------|-------------|
| `make dev` | Start both development servers concurrently |
| `make dev-server` | Start Python server with hot reload (port 8000) |
| `make dev-ui` | Start Rust UI in development mode |
| `make run` | Alias for dev |

**Development servers:**
- **Python Server**: Runs on `http://localhost:8000` with uvicorn auto-reload
- **Rust UI**: Runs with cargo in development mode

### 🔨 Building

| Command | Description |
|---------|-------------|
| `make build` | Build all components |
| `make build-server` | Compile Python server files |
| `make build-ui` | Build Rust UI in debug mode |
| `make build-release` | Build optimized release versions |

### 🧪 Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests (Python + Rust) |
| `make test-server` | Run Python tests with pytest |
| `make test-ui` | Run Rust tests with cargo |
| `make test-watch` | Run Rust tests in watch mode |

### 🔍 Code Quality

| Command | Description |
|---------|-------------|
| `make lint` | Run linters on all code and auto-fix issues |
| `make lint-server` | Run Ruff linter/formatter on Python code |
| `make lint-ui` | Run Clippy and rustfmt on Rust code |
| `make format` | Format all code |
| `make check` | Check code quality without fixing |
| `make pre-commit` | Run pre-commit checks manually |

**Code quality tools:**
- **Python**: Ruff for linting and formatting
- **Rust**: Clippy for linting, rustfmt for formatting

### 🗄️ Database and Services

| Command | Description |
|---------|-------------|
| `make db-up` | Start database services (Docker Compose) |
| `make db-down` | Stop database services |
| `make db-reset` | Reset database (down + up) |

### 🚀 Deployment

| Command | Description |
|---------|-------------|
| `make deploy-staging` | Deploy to staging environment |
| `make deploy-prod` | Deploy to production environment |

*Note: Deployment commands are placeholders and need configuration.*

### 🧹 Maintenance

| Command | Description |
|---------|-------------|
| `make clean` | Clean all build artifacts and caches |
| `make clean-server` | Clean Python artifacts (__pycache__, .pyc files) |
| `make clean-ui` | Clean Rust artifacts (target/ directory) |
| `make update` | Update all dependencies |
| `make reset` | Reset development environment (clean + setup) |

### 📚 Documentation

| Command | Description |
|---------|-------------|
| `make docs` | Generate documentation |
| `make docs-ui` | Generate and open Rust documentation |

### 🛠️ Utilities

| Command | Description |
|---------|-------------|
| `make logs` | Show application logs (Docker Compose) |
| `make ps` | Show running async processes |
| `make env` | Display environment information |
| `make status` | Show comprehensive development status |

### 🔄 CI/CD Simulation

| Command | Description |
|---------|-------------|
| `make ci` | Run complete CI pipeline locally |
| `make all` | Alias for ci |

**CI Pipeline includes:**
1. Code quality checks
2. All tests
3. Build verification

## Dependencies

### Required Tools

- **Python 3.8+**: For server development
- **UV**: Python package manager and virtual environment tool
- **Rust**: For UI development
- **Cargo**: Rust package manager (comes with Rust)
- **Git**: Version control
- **Docker** (optional): For database services

### Installation Verification

Run `make env` to verify all required tools are installed:

```bash
make env
```

## Development Workflow

### For New Developers

1. **Initial Setup**:
   ```bash
   git clone <repository>
   cd async-agent-system
   make setup
   ```

2. **Daily Development**:
   ```bash
   make dev          # Start development servers
   # Make your changes
   make test         # Run tests
   make lint         # Check/fix code quality
   ```

3. **Before Committing**:
   ```bash
   make ci           # Run full CI pipeline
   git add .
   git commit -m "Your changes"
   ```

### For Experienced Developers

- Use `make quick-start` for rapid environment setup
- Use `make test-watch` for TDD workflow
- Use `make status` to check project health

## Parallel Execution

The Makefile uses parallel execution for efficiency:
- `make dev` runs server and UI concurrently using `-j2`
- Individual components can be started separately if needed

## Error Handling

- Commands include proper error handling and informative output
- Failed commands will stop execution with clear error messages
- Use `make clean` followed by `make setup` to recover from build issues

## Customization

The Makefile is designed to be extensible. Common customizations:

1. **Add new environments**: Extend deployment targets
2. **Add new tools**: Include additional linters or formatters
3. **Modify ports**: Change default development server ports
4. **Add services**: Include additional database or service commands

## Troubleshooting

### Common Issues

1. **UV not found**: Install UV using `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Rust not found**: Install Rust using `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
3. **Permission errors**: Ensure proper file permissions for scripts
4. **Port conflicts**: Check if ports 8000 (server) are available

### Getting Help

- Run `make help` for a quick command reference
- Run `make status` for current project status
- Check individual component READMEs in `packages/server/` and `packages/ui/`

## Performance Tips

- Use `make build-release` for production builds
- Use `make test-watch` during active development
- Run `make clean` periodically to free disk space
- Use `make update` regularly to keep dependencies current

## Integration with IDEs

The Makefile integrates well with various IDEs:
- **VS Code**: Use tasks.json to integrate make commands
- **IntelliJ/PyCharm**: Configure external tools for make commands
- **Vim/Neovim**: Use make integration plugins

## Contributing

When adding new make targets:
1. Include helpful descriptions using `## comment`
2. Group related commands in sections
3. Use consistent naming conventions
4. Test on clean environments
5. Update this documentation
