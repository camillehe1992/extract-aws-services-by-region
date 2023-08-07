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
