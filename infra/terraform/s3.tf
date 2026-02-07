resource "aws_s3_bucket" "data_bucket" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_notification" "api_json_events" {
  bucket = aws_s3_bucket.data_bucket.id

  queue {
    queue_arn    = aws_sqs_queue.api_events.arn
    events       = ["s3:ObjectCreated:*"]
    filter_prefix = "bls/api/"
    filter_suffix = ".json"
  }
}
