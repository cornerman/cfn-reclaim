NAME=cfn-reclaim-provider
VERSION=0.1.0
AWS_REGION=eu-central-1
ALL_REGIONS=$(shell printf "import boto3\nprint('\\\n'.join(map(lambda r: r['RegionName'], boto3.client('ec2').describe_regions()['Regions'])))\n" | python | grep -v '^$(AWS_REGION)$$')

help:
	@echo 'make clean                  - the workspace.'
	@echo 'make build                  - build zip file'
	@echo 'make test                   - execute the tests, requires a working AWS connection.'
	@echo 'make deploy-provider-bucket - deploys the provider.'
	@echo 'make delete-provider-bucket - deploys the provider.'
	@echo 'make deploy-provider        - deploys the provider.'
	@echo 'make delete-provider        - deletes the provider.'
	@echo 'make demo                   - deploys the provider and the demo cloudformation stack.'
	@echo 'make delete-demo            - deletes the demo cloudformation stack.'

build: target/$(NAME)-$(VERSION).zip

target/$(NAME)-$(VERSION).zip: src/*.py requirements.txt
	mkdir -p target/content
	docker build --build-arg ZIPFILE=$(NAME)-$(VERSION).zip -t $(NAME)-lambda:$(VERSION) -f Dockerfile.lambda . && \
		ID=$$(docker create $(NAME)-lambda:$(VERSION) /bin/true) && \
		docker export $$ID | (cd target && tar -xvf - $(NAME)-$(VERSION).zip) && \
		docker rm -f $$ID && \
		chmod ugo+r target/$(NAME)-$(VERSION).zip

clean:
	rm -rf target src/*.pyc

test:
	for n in ./cloudformation/*.yaml ; do aws cloudformation validate-template --template-body file://$$n ; done
	. ./venv/bin/activate && \

deploy-provider-bucket: build
	aws --region $(AWS_REGION) cloudformation deploy \
                --capabilities CAPABILITY_IAM \
                --stack-name $(NAME)-bucket \
                --template-file cloudformation/cfn-resource-provider-bucket.yaml \
                --parameter-overrides S3BucketName=$(NAME) || true
	aws --region $(AWS_REGION) s3 sync target/ s3://$(NAME)/lambdas/

delete-provider-bucket:
	aws --region $(AWS_REGION) cloudformation delete-stack --stack-name $(NAME)-bucket

deploy-provider: deploy-provider-bucket
	aws --region $(AWS_REGION) cloudformation deploy \
                --capabilities CAPABILITY_IAM \
                --stack-name $(NAME) \
                --template-file cloudformation/cfn-resource-provider.yaml \
                --parameter-overrides S3BucketName=$(NAME) S3Key=lambdas/$(NAME)-$(VERSION).zip || true

delete-provider:
	aws --region $(AWS_REGION) cloudformation delete-stack --stack-name $(NAME)

demo: deploy-provider
	aws --region $(AWS_REGION) cloudformation deploy \
                --capabilities CAPABILITY_IAM \
                --stack-name $(NAME)-demo2 \
                --template-file cloudformation/demo-stack.yaml \
                --parameter-overrides BucketName=$(NAME)-demo-bucket RepositoryName=$(NAME)-demo-repository || true

delete-demo:
	aws --region $(AWS_REGION) cloudformation delete-stack --stack-name $(NAME)-demo2

