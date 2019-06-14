# Custom::Reclaim::S3::Bucket
The `Custom::Reclaim::S3::Bucket` just acts like a normal `AWS::S3::Bucket`, with one exception: If the s3 bucket with this name already exists, it will just use the existing s3 bucket instead of failing the update. You can furthermore configure whether specific tag needs to be set on the bucket in order to be claimed by this bucket. It can additionally not be part of another cloudformation stack.


## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
  Bucket:
    Type: Custom::ReclaimS3Bucket
    Properties:
      BucketName: !Ref BucketName
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-reclaim-provider-function'
      ReclaimTags:
        - Name: StackName
          Value: ${AWS::StackName}
```

## Properties
You can specify the same properties as on normal S3 Bucket with the additional properties:

    "ServiceToken" - pointing to the function implementing this resource (required).
    "ReclaimTags" - optional set of tags that need to be defined on the resource in order to be claimed (optional).

## Return value
The resource returns the ARN of the S3 Bucket
