output "lambda_name" {
  value = aws_lambda_function.ingestion.function_name
}

output "sqs_queue_url" {
  value = aws_sqs_queue.api_events.id
}
