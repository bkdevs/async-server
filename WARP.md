# Async Agent System - Warp Agent Guidelines

This document provides guidance for Warp agents working with the async-agent-system project, an open-source AI coding tool that integrates Claude Code with task management and code review workflows.

## Project Overview

**async-agent-system** is a developer tool that combines AI coding capabilities with task management and code review. It integrates Claude Code + Linear + GitHub PRs into one opinionated workflow, executing code changes in isolated cloud environments while handling the full development lifecycle from GitHub issues to merged PRs.

### Key Features
- **Automatic research** - analyzes codebases and asks clarifying questions before execution
- **Cloud execution** - runs in isolated Google Cloud Run environments
- **Reviewable subtasks** - creates stack diffs for easier code review  
- **Full workflow automation** - from GitHub issue to merged PR

## Architecture

This is a **monorepo** with two main packages:

### 1. Server (`packages/server/`)
- **Language**: Python 3.12+
- **Framework**: FastAPI with async support
- **Package Manager**: uv (modern Python package manager)
- **Database**: Firebase Firestore
- **AI Models**: Claude Code, OpenAI, Anthropic, Google AI models
- **Cloud**: Google Cloud Platform with Cloud Run jobs
- **Integrations**: GitHub App, Stripe payments, email notifications

### 2. UI (`packages/ui/`)  
- **Language**: Rust
- **Framework**: Iced (cross-platform GUI framework)
- **Purpose**: Desktop frontend for the agent system
- **Features**: Real-time WebSocket communication, task management UI

## Development Setup

### Server Development

```bash path=/home/userd/Local/async-agent-system/packages/server start=52
# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies  
uv sync

# Setup pre-commit hooks
pre-commit install

# Create environment file (copy from example)
cp .env.example .env
# Edit .env with your API keys
```

**Required Environment Variables:**
- `OPENAI_API_KEY` - OpenAI API access
- `ANTHROPIC_API_KEY` - Claude API access  
- `GOOGLE_API_KEY` - Google AI API access
- `RESEND_API_KEY` - Email service
- `STRIPE_SECRET_KEY` - Payment processing
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook validation
- `GITHUB_WEBHOOK_SECRET` - GitHub webhook validation
- `DB_URI` - Database connection string
- `IS_DEV=True` - Development mode flag

**Additional Setup:**
- Create Firebase config file: `async-firebase.json`
- Grant Google Cloud access: `gcloud auth application-default login`

### UI Development

```bash path=/home/userd/Local/async-agent-system/packages/ui start=null
# Build the UI application
cargo build

# Run in development mode
cargo run

# Build for release
cargo build --release
```

## Development Commands

### Server Commands

```bash path=null start=null
# Start the FastAPI server
uvicorn src.server:app --reload --port 8000

# Run tests
python -m pytest

# Lint and format code
uv run ruff format .
uv run ruff check . --fix

# Run pre-commit hooks manually
pre-commit run --all-files
```

### UI Commands

```bash path=null start=null
# Build the application
cargo build

# Run the application
cargo run  

# Run tests
cargo test

# Check formatting
cargo fmt --check

# Run clippy (Rust linter)
cargo clippy
```

## Key Components & Architecture

### Server Structure (`packages/server/src/`)

- **`server.py`** - Main FastAPI application entry point
- **`api/`** - REST API endpoints organized by domain:
  - `auth/` - Authentication (GitHub OAuth, email verification, invitations)
  - `github/` - GitHub webhook handling and integration
  - `task/` - Task management and scheduling
  - `payment/` - Stripe payment processing
  - `onboarding/` - User onboarding workflows
  - `support/` - Support and contact endpoints
- **`agent/`** - AI agent logic and execution
- **`google/`** - Google Cloud Platform integrations (Cloud Run, Storage, Secrets)
- **`firebase/`** - Firebase Firestore database operations
- **`model/`** - Pydantic data models for API requests/responses
- **`tools/`** - Development tools (filesystem, git operations)
- **`prompt/`** - AI prompts and templates
- **`utils/`** - Shared utilities

### Main API Endpoints

**Authentication:**
- `POST /auth/auth-with-github` - GitHub OAuth completion
- `POST /auth/verify-email` - Send email verification
- `POST /auth/redeem-email-code` - Validate email verification

**GitHub Integration:**
- `POST /github/handle-github-events` - Process webhooks (issues, PRs, push)
- `POST /github/submit-review` - Submit code reviews

**Task Management:**
- `POST /task/schedule-job` - Schedule execution jobs
- `WebSocket /task/chat` - Real-time AI communication

### Google Cloud Run Jobs

The system uses isolated Cloud Run jobs for task processing:

- **`execute-task`** - Main task execution using Claude Code
- **`research-task`** - Codebase analysis and requirement gathering  
- **`revise-task`** - Handle code review feedback
- **`index-project`** - Repository indexing and setup

## Testing & Quality

### Testing

```bash path=null start=null
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov

# Run specific test file
python -m pytest tests/test_specific.py
```

The project uses:
- **pytest** for Python testing with async support (`pytest-asyncio`)
- **mockall** for Rust mocking in tests
- Pre-commit hooks ensure tests pass before commits

### Code Quality

**Python (Server):**
- **Ruff** for linting and formatting (configured in `pyproject.toml`)
- **MyPy** for type checking
- **Pre-commit hooks** for automated quality checks

**Rust (UI):**
- **cargo fmt** for formatting
- **clippy** for linting
- Built-in Rust compiler checks

### Pre-commit Configuration

The server includes comprehensive pre-commit hooks:
- `uv-lock` - Lock dependency versions
- `uv-export` - Export requirements.txt
- `ruff` - Linting with auto-fix
- `ruff-format` - Code formatting
- `pytest` - Run tests (allows exit code 5 for no tests found)

## Best Practices for Agents

### Code Changes
1. **Always read existing code** before making modifications
2. **Follow existing patterns** and conventions in the codebase
3. **Update dependencies** when modifying code with upstream/downstream relationships
4. **Use the existing FastAPI patterns** for new endpoints
5. **Follow Pydantic model conventions** for data validation

### Development Workflow  
1. **Use uv for Python package management** instead of pip/poetry
2. **Run pre-commit hooks** before committing changes
3. **Test both server and UI components** when making cross-cutting changes
4. **Use environment variables** for configuration, never hardcode secrets
5. **Follow the monorepo structure** - keep server and UI code in respective packages

### Testing
1. **Write tests for new functionality** using pytest
2. **Mock external services** (Google Cloud, Firebase, AI APIs) in tests
3. **Test error conditions** and edge cases
4. **Run the full test suite** before submitting changes

### API Development
1. **Follow FastAPI best practices** for endpoint structure
2. **Use Pydantic models** for request/response validation  
3. **Handle errors consistently** with proper HTTP status codes
4. **Document new endpoints** in docstrings
5. **Maintain async/await patterns** throughout the codebase

### AI Integration
1. **Understand the agent execution model** - research → execution → review
2. **Be mindful of API costs** when making AI model calls
3. **Handle AI model failures gracefully** with proper error handling
4. **Test with different AI models** when possible (Claude, OpenAI, Google)

## Common Tasks

### Adding New API Endpoints
1. Create endpoint in appropriate `api/` subdirectory
2. Add Pydantic models in `model/` if needed  
3. Register router in `server.py`
4. Add tests in corresponding test file
5. Update API documentation

### Working with Google Cloud
1. Ensure `gcloud auth application-default login` is configured
2. Use existing clients in `google/` directory
3. Handle cloud service failures gracefully
4. Test locally with cloud service mocks

### Database Operations
1. Use Firebase client patterns from `firebase/` directory
2. Handle Firestore-specific data types properly
3. Implement proper error handling for database operations
4. Consider data consistency in distributed environment

## Deployment

The application is designed for Google Cloud Platform:
- **Cloud Run** for the FastAPI server
- **Cloud Run Jobs** for isolated task execution
- **Firebase Firestore** for data persistence
- **Google Cloud Storage** for file storage
- **Google Secret Manager** for configuration

Environment variables must be configured in the production deployment matching the `.env.example` template.

---

*This is a sophisticated AI coding tool designed for experienced developers. When working with this codebase, always consider the distributed nature of the system and the integration points with external services.*
