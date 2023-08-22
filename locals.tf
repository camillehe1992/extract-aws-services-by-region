locals {
  partition = startswith(var.aws_region, "cn") ? "aws-cn" : "cn"
}
