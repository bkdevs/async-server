import asyncio
from concurrent.futures import ThreadPoolExecutor

from firebase_admin import storage

BUCKET_NAME = "async-ce57e.firebasestorage.app"


class StorageClient:
    """
    Wrapper for Firebase Storage
    """

    def __init__(self):
        self.bucket = storage.bucket(BUCKET_NAME)
        self.executor = ThreadPoolExecutor(max_workers=None)

    async def upload_project_image_async(self, org_id: str, project_id: str, image_blob: str):
        """
        Upload a project image to Firebase Storage.
        """
        blob = self.bucket.blob(f"orgs/{org_id}/projects/{project_id}/image.webp")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self.executor, lambda: blob.upload_from_string(image_blob, content_type="image/webp")
        )
