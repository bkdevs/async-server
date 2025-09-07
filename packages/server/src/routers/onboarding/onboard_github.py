from fastapi import APIRouter, status

from src.api.onboarding import OnboardGithubRequest, OnboardGithubResponse
from src.clients import get_firestore_client, get_github_client, get_secret_client
from src.model.app import Org, OrgType, Profile, User, UserRole
from src.model.github import Installation

router = APIRouter()


@router.post("/onboard-github", status_code=status.HTTP_200_OK)
async def onboard_github_async(request: OnboardGithubRequest) -> OnboardGithubResponse:
    firestore_client = get_firestore_client()
    github_client = get_github_client()
    secret_client = get_secret_client()

    installation = await github_client.get_installation_async(request.installation_id)
    org = await _create_org_async(installation)
    user = await firestore_client.update_user_async(request.user_id, org_id=org.id, role=UserRole.ADMIN)
    await _create_user_profile_async(user, org.id)

    client_id = await secret_client.get_async_github_app_client_id_async()
    client_secret = await secret_client.get_async_github_app_client_secret_async()
    user_access_token = await github_client.get_access_token_async(client_id, client_secret, request.code)
    await secret_client.create_user_github_token_secret_async(request.user_id, user_access_token)

    github_id, github_login = await github_client.get_user_information_async(user_access_token)
    await firestore_client.update_user_async(request.user_id, github_id=github_id, github_login=github_login)

    repos = []
    access_token = await github_client.generate_app_access_token_async(request.installation_id)
    async for repo in github_client.list_installation_repos_async(access_token):
        repos.append(repo)
    repos.sort(key=lambda repo: repo.updated_at, reverse=True)
    return OnboardGithubResponse(repos=repos)


async def _create_org_async(installation: Installation) -> Org:
    account = installation.account
    github_account_type = OrgType.USER if account.type == "User" else OrgType.ORGANIZATION

    org = Org(
        name=account.login,
        github_installation_id=installation.id,
        github_account_type=github_account_type,
        github_account_name=account.login,
        github_avatar_url=account.avatar_url,
        onboarded=False,
    )
    return await get_firestore_client().create_org_async(org)


async def _create_user_profile_async(user: User, org_id: str):
    profile = Profile(
        id=user.id,
        name=user.name,
        email=user.email,
    )
    await get_firestore_client().create_profile_async(org_id, profile)
