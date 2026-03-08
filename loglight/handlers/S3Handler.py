from loglight.handlers.BaseHandler import BaseHandler


class S3Handler(BaseHandler):
    def __init__(self, bucket_name, key_prefix="", aws_region="us-east-1", enable_internal_logging=True):
        super().__init__(enable_internal_logging)
        self.bucket_name = bucket_name
        self.key_prefix = key_prefix
        try:
            import boto3
            self.s3_client = boto3.client('s3', region_name=aws_region)
        except ImportError:
            raise ImportError("boto3 is required for S3Handler. Install with: pip install loglight[s3]")

    def emit(self, log_str: str):
        try:
            import uuid
            key = f"{self.key_prefix}{uuid.uuid4()}.log"
            self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=log_str)
        except Exception as e:
            self.log_internal_error("s3_emit_failed", e, context={"bucket": self.bucket_name})
