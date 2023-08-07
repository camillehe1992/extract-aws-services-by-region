terraform {
  backend "s3" {
    bucket  = "tf-state-210692783429-cn-north-1"
    key     = "extract-services-by-region.json"
    region  = "cn-north-1"
    profile = "210692783429_UserFull"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>5.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  default_tags {
    tags = {
      application = "${var.application_name}"
    }
  }
}

# Create S3 bucket
resource "random_pet" "lambda_bucket_name" {
  prefix = var.application_name
  length = 2
}

resource "aws_s3_bucket" "lambda_bucket" {
  bucket = random_pet.lambda_bucket_name.id
}

# Create and upload Lambda function archive
data "archive_file" "lambda_extractor" {
  type = "zip"

  source_dir  = "${path.module}/build/${var.application_name}"
  output_path = "${path.module}/build/${var.application_name}.zip"
}

resource "aws_s3_object" "lambda_extractor" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "${var.application_name}.zip"
  source = data.archive_file.lambda_extractor.output_path

  etag = filemd5(data.archive_file.lambda_extractor.output_path)
}

# Create the Lambda function

resource "aws_lambda_function" "extractor" {
  function_name = var.application_name

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.lambda_extractor.key

  runtime = "python3.9"
  timeout = 60
  handler = "main.lambda_handler"

  source_code_hash = data.archive_file.lambda_extractor.output_base64sha256

  role = aws_iam_role.lambda_exec.arn

  environment {
    variables = {
      ENV                      = var.environment
      APPLICATION              = var.application_name
      AWS_SERVICES_API_URL     = var.aws_services_api_url
      XLSX_FILE_S3_BUKCET_NAME = aws_s3_bucket.lambda_bucket.id
    }
  }
}

resource "aws_cloudwatch_log_group" "extractor" {
  name = "/aws/lambda/${aws_lambda_function.extractor.function_name}"

  retention_in_days = 30
}

resource "aws_iam_role" "lambda_exec" {
  name = "${var.application_name}-sls-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_lambda" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws-cn:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_policy_s3_ro" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws-cn:iam::aws:policy/AmazonS3FullAccess"
}
