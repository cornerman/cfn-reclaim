# Custom::ReclaimECRRepositoryStatement

The `Custom::ReclaimECRRepositoryStatement` allows you to append/update
statements within an existing RepositoryPolicy. The resource basically allows
you to define multiple repository policies within your cloudformation stack. If
there is no repository policy on an ecr repository, it will add a policy with
your policy statement. If there is an existing repository policy, it will
append your policy statement to the existing statements.

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
  RepositoryPolicy:
    Type: Custom::ReclaimECRRepositoryStatement
    Properties:
      Repsitory: !Ref RepositoryName
      PolicyStatement:
        Sid: "repository-policy-1"
        Effect: "Allow"
        Action:
          - "ecr:*"
        Resource: !Sub "arn:aws:ecr:${AWS::Region}:${AWS::AccountId}:${RepositoryName}"
        Principal:
          AWS: "*"
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-reclaim-provider-function'
```

Be aware, every statement handled by this custom resource needs to have an `Sid` in order to distinguish multiple statements.

## Properties
You can specify the same properties as on normal ECR Repsitory with the additional properties:

    "ServiceToken" - pointing to the function implementing this resource (required).

## Return value
The resource returns the ARN of the ECR Repsitory
