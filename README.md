CloudWatch Event(Bridge) + Lambda + SNS Topic + Email Notification

This repo is a simple event & notification workflow example that deployed in AWS Cloud. It's a totally AWS Cloud native workflow, and all AWS resources are defined and deployed using Terraform.
___

The repo code implements below scenario:

Extract AWS available services by specific regions from AWS official API using AWS Lambda function, then upload the findings to S3 bucket, finally send out a email notification to subscribers with the presigned url of findings file in S3 bucket. The entire workflow is triggered as scheduled using CloudWatch Event (Bridge).

Below is the workflow diagram. The core functionality is defined in Lambda function, including extract data, upload file to S3 bucket, generate pre-signed url, etc. You can create your own workflow following the example, only need to change the Lambda function core code as you need. CloudWatch scheduled rule cron expression and email notification address can be configured in *variables.tf*. 

![workflow diagram](cw_bridge_lambda_sns.png)


## Code Structure
```bash
.
├── Pipfile                         # pipenv file to save dependencies
├── Pipfile.lock
├── README.md
├── cloudformation                  # The AWS resources' CloudFormation to save terrafrom state file and lock file
│   └── tf_infrastructure.yaml
├── extract-services-by-region      # Lambda function source code and requirements.txt
│   ├── main.py
│   └── requirements.txt
├── main.tf                         # main.tf, outputs.tf, variables.tf are all Terrform related definitions
├── makefile                        # A makefile to make command life easily
├── outputs.tf
└── variables.tf
```
Notes:
- tf_infrastructure.yaml: Terrform use S3 bucket and Dynamodb table to save state and lock files. That is why I create a CloudFormation template here. You can create these resources manually from AWS console as well. Then update `bucket` and `key` field in below block in *main.tf*.
```yaml
  backend "s3" {
    bucket  = "tf-state-210692783429-cn-north-1"
    key     = "extract-services-by-region.json"
  }
```
- All AWS resources are defined in `main.tf`.
- Always remember to add denpendencies in `requirements.txt` if you are sure that is necessary for Lambda function.

## Local Development
In order to debug and test your Lambda code locally, firstly you should create a vitual environment for it. In the example, we use _python_ as the language, so I chose *pipenv* to setup a vitual environment and install python dependencies in it. Run below command.
```bash
# Install pipenv on local machine
make install

# Create a vitual environment and install dependencies in Pipfile
make dev
```
## Deployment

### Deploy from Local
Deploy the application to AWS using terraform CLI

```bash
make init

make plan

make apply
```

Once Terraform creates the function, invoke it using the AWS CLI. The output will be saved into *response.json*

```bash
AWS_PROFILE=210692783429_UserFull aws lambda invoke \
    --function-name=$(terraform output -raw function_name) response.json
```
Then, download the xlsx file with AWS available services by specific regions information from the URL using below command.
```bash
cat response.json | jq .body
```

# Deploy via GitHub Actions


## Reference
https://developer.hashicorp.com/terraform/tutorials/aws/lambda-api-gateway#lambda-api-gateway
