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

# Configure public access block to allow public access
resource "aws_s3_bucket_public_access_block" "data_bucket_pab" {
  bucket = aws_s3_bucket.data_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Bucket policy to allow public read access
resource "aws_s3_bucket_policy" "data_bucket_policy" {
  bucket = aws_s3_bucket.data_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.data_bucket.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.data_bucket_pab]
}