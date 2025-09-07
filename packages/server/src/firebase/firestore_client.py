from typing import Optional

from firebase_admin import firestore, firestore_async

from google.api_core import retry
from google.api_core.exceptions import Unknown
from src.model.app import Org, Profile, User
from src.model.app.project import Project, Repository
from src.model.app.task import Message, MessageEvent, PullRequest, Subtask, Task
from src.model.auth import EmailCode, Invite
from src.model.payment import StripeCustomer
from src.model.slack import SlackCustomer
from src.model.support import Lead

firestore_retry = retry.AsyncRetry(predicate=retry.if_exception_type(Unknown))


class FirestoreClient:
    """
    Asynchronous wrapper client for Google Cloud Firestore operations.
    Provides CRUD operations for all application entities with consistent error handling.
    """

    def __init__(self):
        self.client = firestore_async.client()

    # ========================================
    # USER OPERATIONS
    # ========================================

    @firestore_retry
    async def create_user_async(self, user: User) -> User:
        user_col_ref = self.client.collection("users")
        user_doc_ref = user_col_ref.document(user.id)
        await user_doc_ref.set(user.model_dump())
        return user

    @firestore_retry
    async def get_user_async(self, user_id: str) -> User:
        user_col_ref = self.client.collection("users")
        user_doc_ref = user_col_ref.document(user_id)
        user_doc = await user_doc_ref.get()
        return User(**user_doc.to_dict())

    @firestore_retry
    async def update_user_async(self, user_id: str, **kwargs) -> User:
        user_col_ref = self.client.collection("users")
        user_doc_ref = user_col_ref.document(user_id)
        await user_doc_ref.update(kwargs)
        updated_user_doc = await user_doc_ref.get()
        return User(**updated_user_doc.to_dict())

    @firestore_retry
    async def add_user_subscribed_task_async(self, user_id: str, task_id: str) -> None:
        user_col_ref = self.client.collection("users")
        user_doc_ref = user_col_ref.document(user_id)
        await user_doc_ref.update({"subscribed_tasks": firestore.ArrayUnion([task_id])})

    @firestore_retry
    async def get_users_in_org_async(self, org_id: str) -> list[User]:
        user_col_ref = self.client.collection("users")
        user_docs = await user_col_ref.where("org_id", "==", org_id).get()
        return [User(**user_doc.to_dict()) for user_doc in user_docs]

    # ========================================
    # PROFILE OPERATIONS
    # ========================================

    @firestore_retry
    async def create_profile_async(self, org_id: str, profile: Profile) -> Profile:
        profile_doc_ref = self.client.document(f"orgs/{org_id}/profiles/{profile.id}")
        await profile_doc_ref.set(profile.model_dump())
        return profile

    @firestore_retry
    async def get_profile_async(self, org_id: str, user_id: str) -> Profile:
        profile_doc_ref = self.client.document(f"orgs/{org_id}/profiles/{user_id}")
        profile_doc = await profile_doc_ref.get()
        return Profile(**profile_doc.to_dict())

    # ========================================
    # ORGANIZATION OPERATIONS
    # ========================================

    @firestore_retry
    async def create_org_async(self, org: Org) -> Org:
        org_col_ref = self.client.collection("orgs")
        org_doc_ref = org_col_ref.document(org.id)
        await org_doc_ref.set(org.model_dump())
        return org

    @firestore_retry
    async def update_org_async(self, org_id: str, **kwargs) -> None:
        org_col_ref = self.client.collection("orgs")
        org_doc_ref = org_col_ref.document(org_id)
        await org_doc_ref.update(kwargs)

    @firestore_retry
    async def get_org_async(self, org_id: str) -> Org:
        org_col_ref = self.client.collection("orgs")
        org_doc_ref = org_col_ref.document(org_id)
        org_doc = await org_doc_ref.get()
        return Org(**org_doc.to_dict())

    # ========================================
    # PROJECT OPERATIONS
    # ========================================

    @firestore_retry
    async def create_project_async(self, org_id: str, project: Project) -> Project:
        project_col_ref = self.client.collection(f"orgs/{org_id}/projects")
        project_doc_ref = project_col_ref.document(project.id)
        await project_doc_ref.set(project.model_dump())
        return project

    @firestore_retry
    async def get_project_async(self, org_id: str, project_id: str) -> Project:
        proj_col_ref = self.client.collection(f"orgs/{org_id}/projects")
        proj_doc_ref = proj_col_ref.document(project_id)
        proj_doc = await proj_doc_ref.get()
        return Project(**proj_doc.to_dict())

    @firestore_retry
    async def get_projects_async(self, org_id: str) -> list[Project]:
        proj_col_ref = self.client.collection(f"orgs/{org_id}/projects")
        proj_docs = await proj_col_ref.get()
        return [Project(**proj_doc.to_dict()) for proj_doc in proj_docs]

    @firestore_retry
    async def update_project_async(self, org_id: str, project_id: str, **kwargs) -> None:
        proj_col_ref = self.client.collection(f"orgs/{org_id}/projects")
        proj_doc_ref = proj_col_ref.document(project_id)
        await proj_doc_ref.update(kwargs)

    # ========================================
    # TASK OPERATIONS
    # ========================================

    @firestore_retry
    async def create_task_async(self, org_id: str, task: Task) -> Task:
        task_col_ref = self.client.collection(f"orgs/{org_id}/tasks")
        task_doc_ref = task_col_ref.document(task.id)
        await task_doc_ref.set(task.model_dump())
        return task

    @firestore_retry
    async def get_task_async(self, org_id: str, task_id: str) -> Task:
        task_col_ref = self.client.collection(f"orgs/{org_id}/tasks")
        task_doc_ref = task_col_ref.document(task_id)
        task_doc = await task_doc_ref.get()
        return Task(**task_doc.to_dict())

    @firestore_retry
    async def get_task_by_github_id_async(self, org_id: str, github_issue_id: int) -> Optional[Task]:
        task_col_ref = self.client.collection(f"orgs/{org_id}/tasks")
        task_docs = await task_col_ref.where("github_issue_id", "==", github_issue_id).get()
        if not task_docs:
            return None
        return Task(**task_docs[0].to_dict())

    @firestore_retry
    async def update_task_async(self, org_id: str, task_id: str, **kwargs) -> None:
        task_col_ref = self.client.collection(f"orgs/{org_id}/tasks")
        task_doc_ref = task_col_ref.document(task_id)
        await task_doc_ref.update(kwargs)

    @firestore_retry
    async def delete_task_async(self, org_id: str, task_id: str) -> None:
        task_col_ref = self.client.collection(f"orgs/{org_id}/tasks")
        task_doc_ref = task_col_ref.document(task_id)
        await task_doc_ref.delete()

    # ========================================
    # SUBTASK OPERATIONS
    # ========================================

    @firestore_retry
    async def create_subtask_async(self, org_id: str, task_id: str, subtask: Subtask) -> Subtask:
        subtask_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/subtasks")
        subtask_doc_ref = subtask_col_ref.document(subtask.id)
        await subtask_doc_ref.set(subtask.model_dump())
        return subtask

    @firestore_retry
    async def get_subtask_async(self, org_id: str, task_id: str, subtask_id: str) -> Subtask:
        subtask_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/subtasks")
        subtask_doc_ref = subtask_col_ref.document(subtask_id)
        subtask_doc = await subtask_doc_ref.get()
        return Subtask(**subtask_doc.to_dict())

    @firestore_retry
    async def get_subtasks_async(self, org_id: str, task_id: str) -> list[Subtask]:
        subtask_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/subtasks")
        subtask_docs = await subtask_col_ref.order_by("created_at", direction=firestore.Query.ASCENDING).get()
        return [Subtask(**subtask_doc.to_dict()) for subtask_doc in subtask_docs]

    @firestore_retry
    async def get_latest_subtask_async(self, org_id: str, task_id: str) -> Subtask:
        subtask_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/subtasks")
        subtask_docs = await subtask_col_ref.order_by("created_at", direction=firestore.Query.DESCENDING).limit(1).get()
        return Subtask(**subtask_docs[0].to_dict())

    @firestore_retry
    async def update_subtask_async(self, org_id: str, task_id: str, subtask_id: str, **kwargs) -> None:
        subtask_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/subtasks")
        subtask_doc_ref = subtask_col_ref.document(subtask_id)
        await subtask_doc_ref.update(kwargs)

    @firestore_retry
    async def delete_subtask_async(self, org_id: str, task_id: str, subtask_id: str) -> None:
        subtask_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/subtasks")
        subtask_doc_ref = subtask_col_ref.document(subtask_id)
        await subtask_doc_ref.delete()

    # ========================================
    # MESSAGE OPERATIONS
    # ========================================

    @firestore_retry
    async def create_message_async(self, org_id: str, task_id: str, message: Message) -> Message:
        message_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/messages")
        message_doc_ref = message_col_ref.document(message.id)
        await message_doc_ref.set(message.model_dump())
        return message

    @firestore_retry
    async def get_latest_message_async(self, org_id: str, task_id: str) -> Message:
        message_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/messages")
        message_docs = await message_col_ref.order_by("created_at", direction=firestore.Query.DESCENDING).limit(1).get()
        return Message(**message_docs[0].to_dict())

    @firestore_retry
    async def get_messages_async(self, org_id: str, task_id: str) -> list[Message]:
        message_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/messages")
        message_docs = await message_col_ref.order_by("created_at", direction=firestore.Query.ASCENDING).get()
        return [Message(**message_doc.to_dict()) for message_doc in message_docs]

    @firestore_retry
    async def update_message_async(self, org_id: str, task_id: str, message_id: str, **kwargs) -> None:
        message_col_ref = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/messages")
        message_doc_ref = message_col_ref.document(message_id)
        await message_doc_ref.update(kwargs)

    # ========================================
    # MESSAGE EVENT OPERATIONS
    # ========================================

    @firestore_retry
    async def create_message_event_async(
        self, org_id: str, task_id: str, parent_message_id: str, message_event: MessageEvent
    ) -> MessageEvent:
        message_events = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/messages/{parent_message_id}/events")
        doc = message_events.document(message_event.id)
        await doc.set(message_event.model_dump())
        return message_event

    @firestore_retry
    async def get_message_events_async(self, org_id: str, task_id: str, parent_message_id: str) -> list[MessageEvent]:
        message_events = self.client.collection(f"orgs/{org_id}/tasks/{task_id}/messages/{parent_message_id}/events")
        message_events_docs = await message_events.get()
        return [MessageEvent(**message_event_doc.to_dict()) for message_event_doc in message_events_docs]

    @firestore_retry
    async def update_message_event_async(
        self, org_id: str, task_id: str, parent_message_id: str, message_event_id: str, **kwargs
    ) -> None:
        message_events_col_ref = self.client.collection(
            f"orgs/{org_id}/tasks/{task_id}/messages/{parent_message_id}/events"
        )
        message_event_doc_ref = message_events_col_ref.document(message_event_id)
        await message_event_doc_ref.update(kwargs)

    # ========================================
    # PULL REQUEST OPERATIONS
    # ========================================

    @firestore_retry
    async def create_pull_request_async(self, pull_request: PullRequest) -> PullRequest:
        pull_request_col_ref = self.client.collection("prs")
        pull_request_doc_ref = pull_request_col_ref.document(pull_request.id)
        await pull_request_doc_ref.set(pull_request.model_dump())
        return pull_request

    @firestore_retry
    async def get_pull_request_async(self, pull_request_id: str) -> Optional[PullRequest]:
        pull_request_col_ref = self.client.collection("prs")
        pull_request_doc_ref = pull_request_col_ref.document(pull_request_id)
        pull_request_doc = await pull_request_doc_ref.get()
        if not pull_request_doc.exists:
            return None
        return PullRequest(**pull_request_doc.to_dict())

    @firestore_retry
    async def update_pull_request_async(self, pull_request_id: str, **kwargs) -> None:
        pull_request_col_ref = self.client.collection("prs")
        pull_request_doc_ref = pull_request_col_ref.document(pull_request_id)
        await pull_request_doc_ref.update(kwargs)

    # ========================================
    # REPOSITORY OPERATIONS
    # ========================================

    @firestore_retry
    async def create_repository_async(self, repository: Repository) -> Repository:
        repo_col_ref = self.client.collection("repos")
        repo_doc_ref = repo_col_ref.document(repository.id)
        await repo_doc_ref.set(repository.model_dump())
        return repository

    @firestore_retry
    async def get_repository_async(self, repository_id: str) -> Optional[Repository]:
        repo_col_ref = self.client.collection("repos")
        repo_doc_ref = repo_col_ref.document(repository_id)
        repo_doc = await repo_doc_ref.get()
        if not repo_doc.exists:
            return None
        return Repository(**repo_doc.to_dict())

    # ========================================
    # AUTH OPERATIONS
    # ========================================

    @firestore_retry
    async def create_email_code_async(self, email_code: EmailCode) -> EmailCode:
        email_code_col_ref = self.client.collection("email_codes")
        email_code_doc_ref = email_code_col_ref.document(email_code.id)
        await email_code_doc_ref.set(email_code.model_dump())
        return email_code

    @firestore_retry
    async def get_email_code_async(self, code: str) -> Optional[EmailCode]:
        email_code_col_ref = self.client.collection("email_codes")
        email_code_docs = email_code_col_ref.where(filter=firestore.FieldFilter("code", "==", code)).limit(1)
        async for doc in email_code_docs.stream():
            return EmailCode(**doc.to_dict())
        return None

    @firestore_retry
    async def update_email_code_async(self, email_code_id: str, **kwargs) -> None:
        email_code_col_ref = self.client.collection("email_codes")
        email_code_doc_ref = email_code_col_ref.document(email_code_id)
        await email_code_doc_ref.update(kwargs)

    @firestore_retry
    async def create_invites_async(self, invites: list[Invite]) -> list[Invite]:
        batch = self.client.batch()
        for invite in invites:
            doc_ref = self.client.document(f"invites/{invite.id}")
            batch.set(doc_ref, invite.model_dump())
        await batch.commit()
        return invites

    @firestore_retry
    async def get_invite_async(self, code: str) -> Optional[Invite]:
        invite_col_ref = self.client.collection("invites")
        query = invite_col_ref.where("code", "==", code)
        docs = [doc async for doc in query.stream()]
        if docs:
            return Invite(**docs[0].to_dict())
        return None

    # ========================================
    # LEAD OPERATIONS
    # ========================================

    @firestore_retry
    async def create_lead_async(self, lead: Lead) -> Lead:
        lead_col_ref = self.client.collection("leads")
        lead_doc_ref = lead_col_ref.document(lead.id)
        await lead_doc_ref.set(lead.model_dump())
        return lead

    # ========================================
    # STRIPE CUSTOMER OPERATIONS
    # ========================================

    @firestore_retry
    async def create_stripe_customer_async(self, stripe_customer: StripeCustomer) -> StripeCustomer:
        stripe_customer_col_ref = self.client.collection("stripe")
        stripe_customer_doc_ref = stripe_customer_col_ref.document(stripe_customer.id)
        await stripe_customer_doc_ref.set(stripe_customer.model_dump())
        return stripe_customer

    @firestore_retry
    async def get_stripe_customer_async(self, stripe_id: str) -> Optional[StripeCustomer]:
        stripe_customer_col_ref = self.client.collection("stripe")
        stripe_customer_doc_ref = stripe_customer_col_ref.document(stripe_id)
        stripe_customer_doc = await stripe_customer_doc_ref.get()
        if not stripe_customer_doc.exists:
            return None
        return StripeCustomer(**stripe_customer_doc.to_dict())

    # ========================================
    # SLACK CUSTOMER OPERATIONS
    # ========================================

    @firestore_retry
    async def create_slack_customer_async(self, slack_customer: SlackCustomer) -> SlackCustomer:
        slack_customer_col_ref = self.client.collection("slack")
        slack_customer_doc_ref = slack_customer_col_ref.document(slack_customer.id)
        await slack_customer_doc_ref.set(slack_customer.model_dump())
        return slack_customer

    @firestore_retry
    async def get_slack_customer_async(self, slack_id: str) -> Optional[SlackCustomer]:
        slack_customer_col_ref = self.client.collection("slack")
        slack_customer_doc_ref = slack_customer_col_ref.document(slack_id)
        slack_customer_doc = await slack_customer_doc_ref.get()
        if not slack_customer_doc.exists:
            return None
        return SlackCustomer(**slack_customer_doc.to_dict())
