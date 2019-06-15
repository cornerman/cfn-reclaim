# Claim existing resources in Cloudformation

**Work in Progress:** Currently not all properties of the resources are supported.

The goal of this project is to allow managing/claiming existing resources within a cloudformation stack.

The following resources are available

- [Custom::ReclaimECRRepository](docs/ReclaimECRRepository.md)
- [Custom::ReclaimS3Bucket](docs/ReclaimS3Bucket.md)
- [Custom::ReclaimS3BucketPolicyStatement](docs/ReclaimS3BucketPolicyStatement.md)

Checkout the example in [cloudformation/demo-stack.yaml](cloudformation/demo-stack.yaml).

## Installation

To install this custom resource:
1) Build zip file `target/cfn-reclaim-provider-0.1.0.zip`: `make build`
2) Upload to your S3 Bucket under some path
3) Deploy lambda functions for custom resource:
```sh
aws cloudformation deploy \
    --capabilities CAPABILITY_IAM \
    --stack-name cfn-reclaim-resource-provider \
    --template-file cloudformation/cfn-resource-provider.yaml
    --parameter-overrides S3BucketName=<your-bucket> S3Key=<path to zip file>/cfn-reclaim-provider-0.1.0.zip
```

## Demo

To deploy a demo stack using these custom resources:

```sh
read -p "bucket name: " BUCKET_NAME
read -p "repository name: " REPO_NAME
aws cloudformation deploy --stack-name reclaim-demo \
	--template-file cloudformation/demo-stack.yaml \
	--parameter-overrides BucketName=BUCKET_NAME RepositoryName=REPO_NAME
```

