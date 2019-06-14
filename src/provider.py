import logging
import s3_bucket_provider
from os import getenv

logging.basicConfig(level=getenv("LOG_LEVEL", "INFO"))

def handler(request, context):
    resource_type = request["ResourceType"]
    print("Got Custom Resource: " + resource_type)
    if resource_type == "Custom::ReclaimS3Bucket":
        return s3_bucket_provider.handler(request, context)
    # elif request["ResourceType"] == "Custom::Existing::ECR::Repository":
    #     return ecr_repository_provider.handler(request, context)
    else:
        raise Exception("Unknown resource name: " + request["ResourceType"])
