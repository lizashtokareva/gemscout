import asyncio
import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from gem_service.config import settings


class S3Storage:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key.get_secret_value(),
            region_name=settings.s3_region,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )

    def generate_upload_url(
        self,
        object_key: str,
        content_type: str,
    ) -> dict:
        return self.client.generate_presigned_post(
            Bucket=settings.s3_bucket,
            Key=object_key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 1, 5 * 1024 * 1024],
            ],
            ExpiresIn=300,
        )

    def generate_object_key(self, gem_id: int, extension: str) -> str:
        return f"gems/{gem_id}/{uuid.uuid4()}.{extension}"

    async def get_object_metadata(self, object_key: str) -> dict | None:
        try:
            return await asyncio.to_thread(
                self.client.head_object(Bucket=settings.s3_bucket, Key=object_key)
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]

        if error_code in ("404", "NoSuchKey", "NotFound"):
            return None
        raise
