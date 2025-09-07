import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.clients import cleanup_clients_async
from src.routers.auth import auth_with_github, invite_people, redeem_email_code, redeem_invite_code, verify_email
from src.routers.github import (
    create_issue,
    create_issue_comment,
    create_pull_request,
    handle_github_events,
    import_issues,
    list_repos,
    submit_review,
    update_issue,
)
from src.routers.onboarding import onboard_github, onboard_projects
from src.routers.payment import create_checkout_session, create_portal_session, handle_stripe_events
from src.routers.slack import handle_slack_events
from src.routers.support import handle_contact_us
from src.routers.task import chat_ws, create_subtasks, schedule_job
from src.utils.bootstrap_utils import bootstrap_application_async, create_bootstrap_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_config = create_bootstrap_config(os.getenv("IS_DEV", "False") == "True")
    await bootstrap_application_async(bootstrap_config)

    yield

    await cleanup_clients_async()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# auth endpoint
app.include_router(auth_with_github.router, prefix="/auth")
app.include_router(invite_people.router, prefix="/auth")
app.include_router(redeem_email_code.router, prefix="/auth")
app.include_router(redeem_invite_code.router, prefix="/auth")
app.include_router(verify_email.router, prefix="/auth")

# github endpoints
app.include_router(create_issue.router, prefix="/github")
app.include_router(create_issue_comment.router, prefix="/github")
app.include_router(create_pull_request.router, prefix="/github")
app.include_router(import_issues.router, prefix="/github")
app.include_router(handle_github_events.router, prefix="/github")
app.include_router(list_repos.router, prefix="/github")
app.include_router(submit_review.router, prefix="/github")
app.include_router(update_issue.router, prefix="/github")

# onboarding endpoints
app.include_router(onboard_github.router, prefix="/onboarding")
app.include_router(onboard_projects.router, prefix="/onboarding")

# payment endpoints
app.include_router(create_checkout_session.router, prefix="/payment")
app.include_router(create_portal_session.router, prefix="/payment")
app.include_router(handle_stripe_events.router, prefix="/payment")

# slack endpoints
app.include_router(handle_slack_events.router, prefix="/slack")

# support endpoints
app.include_router(handle_contact_us.router, prefix="/support")

# task endpoints
app.include_router(chat_ws.router, prefix="/task")
app.include_router(create_subtasks.router, prefix="/task")
app.include_router(schedule_job.router, prefix="/task")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
