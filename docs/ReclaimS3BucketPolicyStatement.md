# Custom::ReclaimS3BucketPolicyStatement

The `Custom::ReclaimS3BucketPolicyStatement` allows you to append/update
statements within an existing BucketPolicy. The resource basically allows you
to define multiple bucket policies within your cloudformation stack. If there
is no bucket policy on an s3 bucket, it will add a policy with your policy
statement. If there is an existing bucket policy, it will append your policy
statement to the existing statements.

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
  BucketPolicy:
    Type: Custom::ReclaimS3BucketPolicyStatement
    Properties:
      Bucket: !Ref BucketName
      PolicyStatement:
        Sid: "bucket-policy-1"
        Effect: "Allow"
        Action:
          - "s3:GetObject"
        Resource: !Sub "arn:aws:s3:::${BucketName}/abcx"
        Principal:
          AWS: "*"
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-reclaim-provider-function'
```

Be aware, every statement handled by this custom resource needs to have an `Sid` in order to distinguish multiple statements.

## Properties
You can specify the same properties as on normal S3 Bucket with the additional properties:

    "ServiceToken" - pointing to the function implementing this resource (required).

## Return value
The resource returns the ARN of the S3 Bucket
