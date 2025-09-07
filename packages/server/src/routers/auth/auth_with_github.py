from fastapi import APIRouter, status

from src.api.auth import AuthGithubRequest, AuthGithubResponse
from src.clients import get_firestore_client, get_github_client, get_secret_client

router = APIRouter()


@router.post("/auth-with-github", status_code=status.HTTP_200_OK)
async def auth_with_github_async(request: AuthGithubRequest) -> AuthGithubResponse:
    github_client = get_github_client()
    secret_client = get_secret_client()

    client_id = await secret_client.get_async_github_app_client_id_async()
    client_secret = await secret_client.get_async_github_app_client_secret_async()
    access_token = await github_client.get_access_token_async(client_id, client_secret, request.code)
    await secret_client.create_user_github_token_secret_async(request.user_id, access_token)

    github_id, github_login = await github_client.get_user_information_async(access_token)
    await get_firestore_client().update_user_async(request.user_id, github_id=github_id, github_login=github_login)
    return AuthGithubResponse()
