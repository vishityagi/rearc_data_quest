resource "aws_sqs_queue" "api_events" {
  name = "rearc-bls-api-json-events"
  visibility_timeout_seconds = 120
}

resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = aws_sqs_queue.api_events.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "s3.amazonaws.com"
      }
      Action   = "sqs:SendMessage"
      Resource = aws_sqs_queue.api_events.arn
      Condition = {
        ArnEquals = {
          "aws:SourceArn" = aws_s3_bucket.data_bucket.arn
        }
      }
    }]
  })
}

resource "aws_lambda_event_source_mapping" "sqs_to_analytics" {
  event_source_arn = aws_sqs_queue.api_events.arn
  function_name    = aws_lambda_function.bls_reports_lambda.arn
  batch_size       = 1
}

