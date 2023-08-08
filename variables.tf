# General deployment variables

variable "aws_region" {
  type        = string
  default     = "cn-north-1"
  description = "AWS region"
}

variable "aws_profile" {
  type        = string
  default     = "210692783429_UserFull"
  description = "AWS profile which is used for the deployment"
}

variable "application_name" {
  type        = string
  default     = "extract-services-by-region"
  description = "The application name"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "The deployment environment"
}

variable "aws_services_api_url" {
  type        = string
  default     = "https://api.regional-table.region-services.aws.a2z.com"
  description = "The API URL to fetch all available AWS Services in all AWS regions"
}

variable "target_regions" {
  type        = string
  default     = "cn-north-1,cn-northwest-1,eu-central-1"
  description = "The target AWS regions that we want to check its AWS services availability"
}

# https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html
variable "cron_expression" {
  type        = string
  default     = "cron(0 8 1 * ? *)"
  description = "The scheduled cron expression, Run at 8:00 am (UTC) every 1st day of the month by default"
}


variable "notification_email_address" {
  type        = string
  default     = "camille.he@outlook.com"
  description = "The email address that subscribes the SNS topic to receive notification"
}
