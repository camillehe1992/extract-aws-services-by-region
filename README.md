Extract AWS available services by specific regions using AWS Lambda function.

## Deploy

Deploy the application to AWS using terraform CLI

```bash

make init

make plan

make apply
```

Once Terraform creates the function, invoke it using the AWS CLI.

```bash
AWS_PROFILE=756143471679_UserFull aws lambda invoke --function-name=$(terraform output -raw function_name) response.json

```

## Reference
https://developer.hashicorp.com/terraform/tutorials/aws/lambda-api-gateway#lambda-api-gateway
