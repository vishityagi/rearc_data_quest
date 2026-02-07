resource "aws_lambda_function" "bls_reports_lambda" {
  function_name = "bls-analytics-consumer"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.14"
  handler       = "app.lambdas.bls_reports_lambda.handler"
  filename      = var.analytics_lambda_zip_path
  source_code_hash = filebase64sha256("../../analytics_consumer_lambda.zip") # Ensures updates are detected when the ZIP file changes

  timeout     = 60
  memory_size = 1024

  layers = [ "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python314:1" ]
  
  environment {
    variables = {
      BLS_BUCKET   = aws_s3_bucket.data_bucket.bucket
      BLS_BASE_URL = "https://download.bls.gov"
      BLS_PREFIX   = "bls/pr/"
    }
  }
}
