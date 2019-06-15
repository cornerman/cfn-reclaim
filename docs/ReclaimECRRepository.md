# Custom::ReclaimECRRepository

The `Custom::ReclaimECRRepository` just acts like a normal
`AWS::ECR::Repository`, with one exception: If the ecr repository with this
name already exists, it will just use the existing ecr repository instead of
failing the update.

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
  Bucket:
    Type: Custom::ReclaimECRRepository
    Properties:
      RepositoryName: !Ref RepositoryName
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-reclaim-provider-function'
```

## Properties
You can specify the same properties as on normal ECR Repository with the additional properties:

    "ServiceToken" - pointing to the function implementing this resource (required).

## Return value
The resource returns the ARN of the ecr repository
