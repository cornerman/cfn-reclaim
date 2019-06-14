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


class ReclaimECRRepository(ResourceProvider):

    def __init__(self):
        super(ReclaimECRRepository, self).__init__()
        self.request_schema = {
            "type": "object",
            "required": ["RepositoryName"],
            "additionalProperties": True,
            "properties": {
                "RepositoryName": {"type": "string", "description": "to create"}
            },
        }

    def create(self):
        try:
            self.create_repository()
        except ClientError as error:
            self.fail("{}".format(error))
            self.physical_resource_id = "failed-to-crate"

    def create_repository(self):
        account_id = provider_helper.get_account_id(self.context)
        region = provider_helper.get_region(self.context)
        repository_name = self.properties['RepositoryName']
        print('Creating ecr repository ' + repository_name)
        repository_arn = "arn:aws:ecr:{}:{}:{}".format(account_id, region, repository_name )

        ecr = boto3.client("ecr", region_name=region)
        try:
            print('Creating new repository')
            arguments={
                'repositoryName': repository_name,
            }
            if "Tags" in self.properties:
                arguments["Tags"] = self.properties["Tags"]
            ecr.create_repository(**arguments)
            self.physical_resource_id = repository_arn
            self.success()
        except ClientError as error:
            print(error.response["Error"]["Message"])
            if error.response["Error"]["Message"] == "The repository with name '{}' already exists in the registry with id '{}'".format(repository_name, account_id):
                print('Repository already exists, will reclaim')
                self.physical_resource_id = repository_arn
                self.success()
            else:
                self.fail("{}".format(error))

    def update(self):
        self.success("nothing to change")

    def delete(self):
        if not self.physical_resource_id or not self.physical_resource_id.startswith("arn:aws:ecr:"):
            print("No physical resource to delete")
            return

        account_id = provider_helper.get_account_id(self.context)
        try:
            print("Deleting ecr-bucket: " + self.physical_resource_id)
            region = self.properties.get("Region")
            ecr = boto3.client("ecr", region_name=region)
            response = ecr.delete_repository(registryId = account_id, repositoryName = self.properties["RepositoryName"])
        except ClientError as error:
          self.success("Cannot delete repository, will retain it: {}".format(error))


provider = ReclaimECRRepository()

def handler(request, context):
    return provider.handle(request, context)
