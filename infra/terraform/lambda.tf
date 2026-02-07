resource "aws_lambda_function" "ingestion" {
  function_name = "bls-ingestion-lambda"
  runtime       = "python3.14"
  role          = aws_iam_role.lambda_role.arn
  handler       = "app.lambdas.ingestion_lambdas.handler"
  filename      = var.lambda_zip_path
  source_code_hash = filebase64sha256("../../bls_ingestion_lambda.zip") # Ensures updates are detected when the ZIP file changes


  timeout      = 120
  memory_size  = 1024

  environment {
    variables = {
      BLS_BUCKET   = aws_s3_bucket.data_bucket.bucket
      BLS_BASE_URL = "https://download.bls.gov"
      BLS_PREFIX   = "bls/pr/"
    }
  }
}
