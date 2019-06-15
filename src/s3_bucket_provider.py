import sys
import time

import os
import boto3
import json
import logging
from botocore.exceptions import ClientError
from cfn_resource_provider import ResourceProvider
import provider_helper

logger = logging.getLogger()


class ReclaimS3BucketProvider(ResourceProvider):

    def __init__(self):
        super(ReclaimS3BucketProvider, self).__init__()
        self.request_schema = {
            "type": "object",
            "required": ["BucketName"],
            "additionalProperties": True,
            "properties": {
                "BucketName": {"type": "string", "description": "to create"}
            },
        }

    def create(self):
        try:
            self.create_bucket()
        except ClientError as error:
            self.fail("{}".format(error))
            self.physical_resource_id = "failed-to-crate"

    def create_bucket(self):
        region = provider_helper.get_region(self.context)
        bucket_name = self.properties['BucketName']
        bucket_arn = "arn:aws:s3:::{}".format(bucket_name)
        print('Creating bucket ' + bucket_name)

        s3 = boto3.client("s3", region_name=region)
        if self.bucket_exists(s3, bucket_name):
          print('Bucket already exists, will reclaim')
          self.physical_resource_id = bucket_arn
          self.success()
        else:
          try:
            print('Creating new bucket')
            arguments={
                'Bucket': bucket_name,
                'CreateBucketConfiguration': {
                    'LocationConstraint': region
                },
            }
            if "AccessControl" in self.properties:
                arguments["ACL"] = self.properties["AccessControl"]
            if "ObjectLockEnabled" in self.properties:
                arguments["ObjectLockEnabledForBucket"] = self.properties["ObjectLockEnabled"]
            s3.create_bucket(**arguments)
            self.physical_resource_id = bucket_arn
            self.success()
          except ClientError as error:
            self.fail("{}".format(error))

    def bucket_exists(self, s3, bucket_name):
        try:
            s3.head_bucket(Bucket=bucket_name)
        except ClientError as error:
            if error.response["Error"]["Message"] == "Not Found":
                return False
            else:
                raise
        return True

    def update(self):
        self.success("nothing to change")

    def delete(self):
        if not self.physical_resource_id or not self.physical_resource_id.startswith("arn:aws:s3:"):
            print("No physical resource to delete")
            return

        try:
            print("Deleting s3-bucket: " + self.physical_resource_id)
            region = self.properties.get("Region")
            s3 = boto3.client("s3", region_name=region)
            response = s3.delete_bucket(Bucket = self.properties["BucketName"])
        except ClientError as error:
          self.success("Cannot delete bucket, will retain it: {}".format(error))


provider = ReclaimS3BucketProvider()

def handler(request, context):
    return provider.handle(request, context)
