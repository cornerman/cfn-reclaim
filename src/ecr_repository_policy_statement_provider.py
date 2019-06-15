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


class ReclaimECRRepositoryPolicyStatementProvider(ResourceProvider):

    def __init__(self):
        super(ReclaimECRRepositoryPolicyStatementProvider, self).__init__()
        self.request_schema = {
            "type": "object",
            "required": ["Repository", "PolicyStatement"],
            "additionalProperties": True,
            "properties": {
                "Repository": {"type": "string", "description": "to create"},
                "PolicyStatement": { "type": "object", "properties": { "Sid": { "type": "string" } } }
            }
        }

    def create(self):
        try:
            self.replaceRepositoryPolicy(replace_sid = None, add_statement = True)
        except ClientError as error:
            self.fail("{}".format(error))
            self.physical_resource_id = "failed-to-crate"

    def replaceRepositoryPolicy(self, replace_sid, add_statement):
        account_id = provider_helper.get_account_id(self.context)
        region = provider_helper.get_region(self.context)
        repository_name = self.properties['Repository']
        repository_arn = "arn:aws:ecr:{}:{}:{}".format(account_id, region, repository_name )
        print('Replacing policy on repository ' + repository_name)

        policy_statement = self.properties['PolicyStatement']
        sid = policy_statement['Sid']
        ecr = boto3.client("ecr", region_name=region)
        try:
            policy_document = self.get_repository_policy(ecr, repository_name, account_id)
            kept_statements = [st for st in policy_document['Statement'] if st['Sid'] != sid and st['Sid'] != replace_sid]
            if add_statement:
                kept_statements.append(policy_statement)

            if kept_statements:
                policy_document['Statement'] = kept_statements
                ecr.set_repository_policy(
                    registryId = account_id,
                    repositoryName = repository_name,
                    policyText = json.dumps(policy_document)
                )
            else:
                ecr.delete_repository_policy(
                    registryId = account_id,
                    repositoryName = repository_name
                )

            self.physical_resource_id = repository_arn
            self.success()
        except ClientError as error:
            self.fail("{}".format(error))

    def get_repository_policy(self, ecr, repository_name, account_id):
        try:
            policy_result = ecr.get_repository_policy(repositoryName = repository_name)
            policy_document_str = policy_result["policyText"]
            return json.loads(policy_document_str)
        except ClientError as error:
            print(error.response["Error"]["Message"])
            if error.response["Error"]["Message"] == "Repository policy does not exist for the repository with name '{}' in the registry with id '{}'".format(repository_name, account_id):
                return self.new_policy_document()
            else:
                raise


    def new_policy_document(self):
        return {
            'Version': "2012-10-17",
            'Statement': []
        }

    def update(self):
        # TODO: handle update of repository
        policy_statement = self.old_properties['PolicyStatement']
        sid = policy_statement['Sid']
        try:
            self.replaceRepositoryPolicy(replace_sid = sid, add_statement = True)
        except ClientError as error:
            self.fail("{}".format(error))

    def delete(self):
        try:
            self.replaceRepositoryPolicy(replace_sid = None, add_statement = False)
        except ClientError as error:
            self.success("Cannot delete bucket policy statement, will retain it: {}".format(error))


provider = ReclaimECRRepositoryPolicyStatementProvider()

def handler(request, context):
    return provider.handle(request, context)
