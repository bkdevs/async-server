from gcloud.aio.storage import Storage

from src.google.gcp_constants import PROJECT_IMAGE_BUCKET_NAME


class StorageClient:
    """
    Wrapper client for Google Cloud Storage
    """

    async def upload_project_image_async(self, org_id: str, project_id: str, image_blob: bytes):
        blob_name = f"orgs/{org_id}/projects/{project_id}/image.webp"
        async with Storage() as storage:
            await storage.upload(
                bucket=PROJECT_IMAGE_BUCKET_NAME, object_name=blob_name, file_data=image_blob, content_type="image/webp"
            )
