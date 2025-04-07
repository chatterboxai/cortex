import os
import boto3
import logging
from fastapi import UploadFile
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Get S3 configuration from environment variables
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_REGION = os.getenv('AWS_REGION')


class S3Service:
    @classmethod
    def get_s3_client(cls):
        """Get a boto3 S3 client with the configured AWS region."""
        return boto3.client('s3', region_name=S3_REGION)
    
    @classmethod
    async def upload_file(cls, file: UploadFile, key: str) -> None:
        content = await file.read()
        
        s3_client = cls.get_s3_client()
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
            Body=content,
            ContentType=file.content_type or 'application/octet-stream'
        )
        
    @classmethod
    def generate_presigned_url(cls, object_key: str, expiry: int = 3600) -> str:
        try:
            s3_client = cls.get_s3_client()
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': S3_BUCKET_NAME,
                    'Key': object_key
                },
                ExpiresIn=expiry
            )
            return url
        except ClientError as e:
            logger.exception(f"Error generating pre-signed URL: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error generating pre-signed URL: {e}")
            raise
