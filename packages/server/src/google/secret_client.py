from async_lru import alru_cache

from google.cloud import secretmanager
from src.google.gcp_constants import (
    ASYNC_GITHUB_APP_CLIENT_ID_KEY,
    ASYNC_GITHUB_APP_CLIENT_SECRET_KEY,
    ASYNC_GITHUB_APP_PRIVATE_KEY_KEY,
    GITHUB_TOKEN_KEY_SUFFIX,
    PROJECT_ID,
)


class SecretClient:
    def __init__(self):
        self.client = secretmanager.SecretManagerServiceAsyncClient()

    @alru_cache
    async def get_async_github_app_client_id_async(self) -> str:
        return await self._get_secret_payload_async(secret_id=ASYNC_GITHUB_APP_CLIENT_ID_KEY)

    @alru_cache
    async def get_async_github_app_client_secret_async(self) -> str:
        return await self._get_secret_payload_async(secret_id=ASYNC_GITHUB_APP_CLIENT_SECRET_KEY)

    @alru_cache
    async def get_async_github_app_private_key_async(self) -> str:
        return await self._get_secret_payload_async(secret_id=ASYNC_GITHUB_APP_PRIVATE_KEY_KEY)

    @alru_cache(ttl=3600)
    async def get_user_github_token_async(self, user_id: str) -> str:
        secret_id = self._get_user_github_token_secret_id(user_id)
        return await self._get_secret_payload_async(secret_id)

    async def create_user_github_token_secret_async(self, user_id: str, github_token: str):
        secret_id = self._get_user_github_token_secret_id(user_id)
        await self.client.create_secret(
            request={
                "parent": f"projects/{PROJECT_ID}",
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            },
        )
        payload = github_token.encode("UTF-8")
        await self.client.add_secret_version(
            request={"parent": f"projects/{PROJECT_ID}/secrets/{secret_id}", "payload": {"data": payload}},
        )

    async def update_user_github_token_secret_async(self, user_id: str, github_token: str):
        secret_id = self._get_user_github_token_secret_id(user_id)
        payload = github_token.encode("UTF-8")
        await self.client.add_secret_version(
            request={"parent": f"projects/{PROJECT_ID}/secrets/{secret_id}", "payload": {"data": payload}},
        )

    async def _get_secret_payload_async(self, secret_id: str, version_id: str = "latest") -> str:
        name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
        response = await self.client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload

    def _get_user_github_token_secret_id(self, user_id: str) -> str:
        return f"{user_id}-{GITHUB_TOKEN_KEY_SUFFIX}"
