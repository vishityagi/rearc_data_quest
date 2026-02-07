resource "aws_sqs_queue" "api_events" {
  name = "rearc-bls-api-json-events"
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
