Extract AWS available services by specific regions using AWS Lambda function.

## Deploy

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

## Reference
https://developer.hashicorp.com/terraform/tutorials/aws/lambda-api-gateway#lambda-api-gateway
