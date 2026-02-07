# Terraform configuration for deploying a Lambda function

provider "aws" {
  region = var.region
}

terraform {
  backend "s3" {
    bucket         = "rearc-terraform-state-bucket"
    key            = "data-pipeline/terraform.tfstate" # Path inside the bucket
    region         = "us-east-1"
    use_lockfile   = true
    encrypt        = true
  }
}