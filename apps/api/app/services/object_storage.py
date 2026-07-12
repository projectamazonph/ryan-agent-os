from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Protocol

import boto3
from botocore.client import BaseClient

from app.core.config import Settings


class ObjectStore(Protocol):
    async def ensure_bucket(self) -> None: ...

    async def put_bytes(
        self,
        key: str,
        body: bytes,
        content_type: str,
        metadata: Mapping[str, str] | None = None,
    ) -> None: ...

    async def get_bytes(self, key: str) -> bytes: ...


class ObjectStorage:
    def __init__(self, settings: Settings) -> None:
        self.bucket = settings.s3_bucket
        self.client: BaseClient = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            use_ssl=settings.s3_secure,
        )

    async def ensure_bucket(self) -> None:
        def ensure() -> None:
            buckets = self.client.list_buckets().get("Buckets", [])
            names = {bucket["Name"] for bucket in buckets}
            if self.bucket not in names:
                self.client.create_bucket(Bucket=self.bucket)

        await asyncio.to_thread(ensure)

    async def put_bytes(
        self, key: str, body: bytes, content_type: str, metadata: Mapping[str, str] | None = None
    ) -> None:
        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=body,
            ContentType=content_type,
            Metadata=dict(metadata or {}),
        )

    async def get_bytes(self, key: str) -> bytes:
        def get() -> bytes:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return bytes(response["Body"].read())

        return await asyncio.to_thread(get)
