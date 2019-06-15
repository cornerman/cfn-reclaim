import logging
import s3_bucket_provider
import s3_bucket_policy_statement_provider
import ecr_repository_provider
from os import getenv

logging.basicConfig(level=getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger()


def handler(request, context):
    resource_type = request["ResourceType"]
    print("Got Custom Resource: " + resource_type)
    if resource_type == "Custom::ReclaimS3Bucket":
        return s3_bucket_provider.handler(request, context)
    elif resource_type == "Custom::ReclaimS3BucketPolicyStatement":
        return s3_bucket_policy_statement_provider.handler(request, context)
    elif resource_type == "Custom::ReclaimECRRepository":
        return ecr_repository_provider.handler(request, context)
    else:
        raise Exception("Unknown resource name: " + request["ResourceType"])
