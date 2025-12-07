import logging
from io import BytesIO
from minio import Minio
from minio.error import S3Error
from app.database import settings

logger = logging.getLogger(__name__)


class StorageService:
    _client = None

    @classmethod
    def get_client(cls) -> Minio:
        """Get or create MinIO client."""
        if cls._client is None:
            cls._client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure
            )
            cls._ensure_bucket_exists()
        return cls._client

    @classmethod
    def _ensure_bucket_exists(cls):
        """Create bucket if it doesn't exist."""
        try:
            if not cls._client.bucket_exists(settings.minio_bucket):
                cls._client.make_bucket(settings.minio_bucket)
                logger.info(f"Created bucket: {settings.minio_bucket}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {str(e)}")
            raise

    @staticmethod
    def upload_file(file_content: bytes, object_name: str) -> str:
        """Upload file to MinIO and return object name."""
        try:
            client = StorageService.get_client()
            client.put_object(
                settings.minio_bucket,
                object_name,
                BytesIO(file_content),
                length=len(file_content)
            )
            logger.info(f"Uploaded file: {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Failed to upload file {object_name}: {str(e)}")
            raise ValueError(f"Failed to upload file to storage: {str(e)}")

    @staticmethod
    def get_file(object_name: str) -> bytes:
        """Download file from MinIO."""
        try:
            client = StorageService.get_client()
            response = client.get_object(settings.minio_bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Failed to get file {object_name}: {str(e)}")
            raise ValueError(f"Failed to retrieve file from storage: {str(e)}")

    @staticmethod
    def delete_file(object_name: str):
        """Delete file from MinIO."""
        try:
            client = StorageService.get_client()
            client.remove_object(settings.minio_bucket, object_name)
            logger.info(f"Deleted file: {object_name}")
        except S3Error as e:
            logger.error(f"Failed to delete file {object_name}: {str(e)}")
