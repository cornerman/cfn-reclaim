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


class ReclaimS3BucketPolicyStatementProvider(ResourceProvider):

    def __init__(self):
        super(ReclaimS3BucketPolicyStatementProvider, self).__init__()
        self.request_schema = {
            "type": "object",
            "required": ["Bucket", "PolicyStatement"],
            "additionalProperties": True,
            "properties": {
                "Bucket": {"type": "string", "description": "to create"},
                "PolicyStatement": { "type": "object", "properties": { "Sid": { "type": "string" } } }
            }
        }

    def create(self):
        try:
            self.replace_bucket_policy(replace_sid = None, add_statement = True)
        except ClientError as error:
            self.fail("{}".format(error))
            self.physical_resource_id = "failed-to-crate"

    def replace_bucket_policy(self, replace_sid, add_statement):
        region = provider_helper.get_region(self.context)
        bucket_name = self.properties['Bucket']
        bucket_arn = "arn:aws:s3:::{}".format(bucket_name)
        print('Replacing bucket policy on bucket ' + bucket_name)

        policy_statement = self.properties['PolicyStatement']
        sid = policy_statement['Sid']
        s3 = boto3.client("s3", region_name=region)
        try:
            policy_document = self.get_bucket_policy(s3, bucket_name)
            kept_statements = [st for st in policy_document['Statement'] if st['Sid'] != sid and st['Sid'] != replace_sid]
            if add_statement:
                kept_statements.append(policy_statement)
            policy_document['Statement'] = kept_statements
            s3.put_bucket_policy(
                Bucket = bucket_name,
                Policy = json.dumps(policy_document)
            )
            self.physical_resource_id = bucket_arn
            self.success()
        except ClientError as error:
            self.fail("{}".format(error))

    def get_bucket_policy(self, s3, bucket_name):
        try:
            policy_result = s3.get_bucket_policy(Bucket = bucket_name)
            policy_document_str = policy_result["Policy"]
            return json.loads(policy_document_str)
        except ClientError as error:
            if error.response["Error"]["Message"] == "The bucket policy does not exist":
                return self.new_policy_document()
            else:
                raise


    def new_policy_document(self):
        return {
            'Version': "2012-10-17",
            'Statement': []
        }

    def update(self):
        policy_statement = self.old_properties['PolicyStatement']
        sid = policy_statement['Sid']
        try:
            self.replace_bucket_policy(replace_sid = sid, add_statement = True)
        except ClientError as error:
            self.fail("{}".format(error))

    def delete(self):
        try:
            self.replace_bucket_policy(replace_sid = None, add_statement = False)
        except ClientError as error:
            self.success("Cannot delete bucket policy statement, will retain it: {}".format(error))


provider = ReclaimS3BucketPolicyStatementProvider()

def handler(request, context):
    return provider.handle(request, context)
