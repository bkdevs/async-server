# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **async-agent-system**, a monorepo containing an AI-powered coding tool that integrates Claude Code with task management and GitHub workflows. The system executes code changes in isolated cloud environments and handles the full development lifecycle from GitHub issues to merged PRs.

## Architecture

### Monorepo Structure
- **`packages/server/`** - Python FastAPI backend (main application)
- **`packages/ui/`** - Rust desktop frontend using Iced framework  
- **`async-frontend/`** - Alternative/legacy frontend (Rust/Iced)

### Server (`packages/server/`)
- **Language**: Python 3.12+
- **Framework**: FastAPI with async support
- **Package Manager**: `uv` (modern Python package manager)
- **Database**: Firebase Firestore
- **Cloud**: Google Cloud Platform with Cloud Run jobs
- **AI Integration**: Claude Code SDK, OpenAI, Anthropic, Google AI models

### Key Cloud Run Jobs
The system uses isolated Google Cloud Run jobs for task processing:
- **`execute-task`** - Main task execution using Claude Code
- **`research-task`** - Codebase analysis and requirement gathering
- **`revise-task`** - Handle code review feedback  
- **`index-project`** - Repository indexing and setup

## Development Commands

### Server Development (from `packages/server/`)

**Setup:**
```bash
# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv sync

# Setup pre-commit hooks
pre-commit install
```

**Core Commands:**
```bash
# Start FastAPI server
uvicorn src.server:app --reload --port 8000

# Run tests
python -m pytest

# Lint and format
uv run ruff format .
uv run ruff check . --fix

# Pre-commit hooks
pre-commit run --all-files
```

### UI Development (from `packages/ui/`)

```bash
# Build application
cargo build

# Run in development
cargo run

# Run tests
cargo test

# Format and lint
cargo fmt --check
cargo clippy
```

## Code Architecture Patterns

### FastAPI Application (`src/server.py`)
- Uses async context manager for lifespan management
- Bootstrap configuration handles dev/prod environments
- Routers organized by domain (auth, github, task, payment, etc.)

### Agent System (`src/agent/`)
- **ClaudeCodeAgent** - Wrapper around Claude Code SDK
- Supports different permission modes and system prompts
- **OutputFormatter** - Handles agent response formatting

### Task Processing Flow
1. **Research Phase** (`src/prompt/research_task_prompt.py`) - Analyzes codebase
2. **Subtask Generation** (`src/prompt/generate_subtasks_prompt.py`) - Breaks down work
3. **Execution** (`src/execute_task.py`) - Runs Claude Code with task prompts
4. **Code Review** - Creates reviewable diffs and handles feedback

### Data Models (`src/model/`)
- **Pydantic models** organized by domain (app, auth, github, payment)
- **Task hierarchy**: Task → Subtask → PullRequest
- **TaskStatus enum**: research, planning, execution, review, completed, failed

### Cloud Integration (`src/google/`)
- **GCR Client** - Google Cloud Run job management
- **Storage Client** - File storage operations
- **Secret Client** - Configuration management

## Development Patterns

### Testing
- Uses `pytest` with `pytest-asyncio` for async testing
- Pre-commit hook allows exit code 5 (no tests found)
- Mock external services (Google Cloud, Firebase, AI APIs)

### Error Handling
- Use Pydantic for input validation
- Handle `ProcessError` from Claude Code SDK with retries
- Consistent HTTP status codes in FastAPI endpoints

### Configuration
- Environment variables for all secrets and configuration
- `.env` file for local development (copy from `.env.example`)
- `async-firebase.json` for Firebase configuration
- `IS_DEV=True` flag for development mode

### Database Operations
- Firebase Firestore with async client patterns
- Models use `generate_id()` for consistent ID generation
- Handle Firestore-specific data types properly

## Key Environment Variables

```bash
# AI APIs
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=

# Services  
STRIPE_SECRET_KEY=
RESEND_API_KEY=
GITHUB_WEBHOOK_SECRET=
DB_URI=

# Development
IS_DEV=True
```

## Working with Claude Code

This system heavily integrates with Claude Code SDK:
- Agent execution happens in isolated cloud environments
- Uses plan mode for breaking down complex tasks
- Handles different permission modes (`acceptEdits`, etc.)
- System and append prompts customize agent behavior

### Common Claude Code Patterns
```python
from claude_code_sdk import ProcessError
from src.agent import ClaudeCodeAgent

agent = ClaudeCodeAgent(
    repo_directory=repo_path,
    system_prompt=system_prompt,
    permission_mode="acceptEdits"
)

try:
    response = await agent.query_async(prompt)
except ProcessError as e:
    # Handle Claude Code execution errors
    logger.error(f"Claude Code error: {e}")
```