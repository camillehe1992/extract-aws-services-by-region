
output "function_name" {
  description = "Name of the Lambda function."
  value       = aws_lambda_function.extractor.function_name
}

output "sns_topic_arn" {
  description = "Name of the SNS topic."
  value       = aws_sns_topic.notification.arn
}
