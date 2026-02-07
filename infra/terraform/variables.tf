// variables.tf
// Define input variables for Terraform

variable "region" {
  default = "us-east-1"
}

variable "bucket_name" {
  description = "S3 bucket name"
}

variable "lambda_zip_path" {
  description = "Path to Lambda ZIP file"
}

variable "analytics_lambda_zip_path" {
  description = "Path to analytics consumer lambda zip"
}

