output "bucket_name" {
  description = "Name of bucket"
  value       = aws_s3_bucket.lambda_bucket.id
}

output "s3_object_key" {
  description = "Key of S3 bucket object that Lambda function uploaded"
  value       = aws_s3_object.lambda_extractor.key
}

output "cloudwatch_rule_arn" {
  description = "ARN of CloudWatch rule that triggers Lambda function"
  value       = aws_cloudwatch_event_rule.rule.arn
}
output "function_name" {
  description = "Name of the Lambda function."
  value       = aws_lambda_function.extractor.function_name
}

output "function_cloudwatch_logs_name" {
  description = "ARN of CloudWatch Logs name of Lambda function"
  value       = aws_cloudwatch_log_group.extractor.arn
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic"
  value       = aws_sns_topic.notification.arn
}
