<div align="center">
  <a href="https://async.build">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/async-logo-dark.png">
      <img src="assets/async-logo-light.png" alt="Async Logo" width="400">
    </picture>
  </a>
</div>

An open-source developer tool that combines AI coding with task management and code review. Async integrates Claude Code + Linear + GitHub PRs into one opinionated workflow.

https://github.com/user-attachments/assets/52e019a0-d42c-4963-af48-cd80bf8b8347

https://www.async.build/

## What Async Does

- **Automatically researches coding tasks** - analyzes your codebase and asks clarifying questions before execution
- **Executes code changes in the cloud** - runs in isolated environments without touching your local setup  
- **Breaks work into reviewable subtasks** - creates stack diffs for easier code review
- **Handles the full workflow** - from GitHub issue to merged PR without leaving the app

## Why Async?

Traditional AI coding tools work great for new projects but struggle with mature codebases where you can't break things. Async solves the common problems:

- **Forces upfront planning** - always asks clarifying questions and requires confirmation before executing
- **Eliminates context switching** - executes asynchronously in the cloud while you work on other tasks
- **Simple task tracking** - automatically imports GitHub issues, no PM tool bloat
- **Built-in code review** - comment and iterate on stacked diffs without leaving the app

## How It Works

1. **Onboarding & Task Creation**: Install the Async GitHub App and select repositories. Async automatically imports open GitHub issues as tasks.

2. **Research Phase**: New tasks trigger a Google Cloud Run job that clones your repository and runs a research agent. The agent analyzes the codebase and generates clarifying questions. Tasks either auto-execute or wait for your input.

3. **Execution**: Another isolated GCR job handles execution using Claude Code. Creates feature branch → breaks task into subtasks → executes each as separate commits → opens PR.

4. **Code Review**: Review happens within Async. Step through each subtask's focused diffs, leave comments, and either request changes (creates new subtask) or approve (squashes and merges).

## Tech Stack

- **Backend**: FastAPI with async support
- **AI Models**: Claude Code for implementation, OpenAI/Anthropic/Google models for research
- **Cloud**: Google Cloud Platform with containerized execution
- **Database**: Firebase Firestore  
- **Integrations**: GitHub App, Stripe payments, email notifications
- **Frontend**: Supports desktop and mobile

## Setup
Create and activate a virtual envirnoment:
```
uv venv .venv
source .venv/bin/activate
```

To explicitly sync the environment, run the following command:
```
uv sync
```

Then run the following to setup pre-commit lints
```
pre-commit install
```

## Local Development
To run the agent locally, create a .env file (look at .env.local for example) in the root directory. 

Create a firebase config file with name "async-firebase.json".

Run the following command to grant the default login to Google Cloud client libraries:
```
gcloud auth application-default login
``` 

To start the server,
```
uvicorn src.server:app --reload --port 8000
```

To lint, run the following command:
```
uv run ruff format .
uv run ruff check . --fix
```

## Testing

To run all unit tests:
```
python -m pytest
```

## API Documentation

The FastAPI server provides the following main endpoints:

### Authentication
- `POST /auth/auth-with-github` - Complete GitHub OAuth flow with access code
- `POST /auth/verify-email` - Send email verification code
- `POST /auth/redeem-email-code` - Validate email verification code
- `POST /auth/invite-people` - Send team invitations
- `POST /auth/redeem-invite-code` - Validate invitation codes

### GitHub Integration  
- `POST /github/handle-github-events` - Process GitHub webhook events (issues, PRs, push)
- `POST /github/submit-review` - Submit code review with approve/request changes

### Task Management
- `POST /task/schedule-job` - Schedule task execution jobs (research, execute, revise, index)
- `WebSocket /task/chat` - Real-time task communication with AI agents

### Onboarding
- `POST /onboarding/onboard-github` - Complete GitHub App installation and repository setup

### Payment
- `POST /payment/create-checkout-session` - Create Stripe checkout for subscriptions
- `POST /payment/create-portal-session` - Access customer billing portal
- `POST /payment/handle-stripe-events` - Process Stripe webhook events

### Support
- `POST /support/handle-contact-us` - Submit contact form and create lead

## Google Cloud Run Jobs

The system uses isolated Google Cloud Run jobs for task processing:

### Job Types
- **`execute-task`** - Main task execution using Claude Code
  - Clones repository to feature branch
  - Breaks task into subtasks using Claude Code plan mode
  - Executes each subtask as separate commit
  - Opens pull request when complete

- **`research-task`** - Codebase analysis and requirement gathering
  - Analyzes repository structure and context
  - Generates clarifying questions for ambiguous requirements
  - Creates structured task summary for execution

- **`revise-task`** - Handles code review feedback
  - Processes review comments and requested changes
  - Creates new subtask to address feedback
  - Re-executes with updated requirements

- **`index-project`** - Repository indexing and setup
  - Analyzes project structure and programming languages
  - Sets up project metadata for task execution
  - Prepares repository for AI agent analysis

Each job runs in an isolated environment with the repository cloned and all necessary dependencies installed.

## Deployment

### Prerequisites
- Google Cloud Platform account with Cloud Run enabled
- Firebase project with Firestore
- GitHub App configured for your organization
- Stripe account for payment processing

### Environment Variables
Configure the following in your production environment:
- `ANTHROPIC_API_KEY` - Claude API access
- `OPENAI_API_KEY` - OpenAI API access  
- `GOOGLE_API_KEY` - Google AI API access
- `STRIPE_SECRET_KEY` - Stripe payment processing
- `GITHUB_WEBHOOK_SECRET` - GitHub webhook validation
- `DB_URI` - Database connection string

### Cloud Deployment
The application is designed to run on Google Cloud Run with automatic scaling and isolated task execution.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure your code follows the existing style and passes all tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please open a GitHub issue or contact the team.

---

*Built for experienced developers who know their codebases deeply. Async is the last tool you'll need to build something great.*
