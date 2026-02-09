# rearc_data_quest

## Rearc Data Quest – Event-Driven Data Pipeline

### Overview

This project implements an event-driven data ingestion and analytics pipeline on AWS using Lambda, S3, SQS, and Terraform.

The solution ingests public datasets from the U.S. Bureau of Labor Statistics (BLS) and the DataUSA API, keeps an S3 bucket in sync with upstream data, and triggers downstream analytics automatically whenever new data is written.

The entire infrastructure is provisioned using Terraform and all compute runs serverlessly on AWS Lambda.

### Architecture

```
BLS Website / DataUSA API
          |
          v
Ingestion Lambda (Part 1 & 2)
          |
          v
   S3 Bucket (rearc-bls-data-sync-lambda)
          |
   (ObjectCreated events)
          |
          v
        SQS Queue
          |
          v
Analytics Lambda (Part 3)
          |
          v
   CloudWatch Logs (Reports)
```

## Part 1 – BLS Dataset Synchronization

### What it does

- Fetches the directory listing from the BLS website
- Discovers files dynamically (no hard-coded filenames)
- Uploads new or updated files to S3
- Deletes files from S3 if they are removed upstream
- Ensures idempotency using metadata-based signatures

### Key Features

- Handles added / removed / updated files
- Avoids duplicate uploads
- Complies with BLS access policies via a descriptive User-Agent
- Normalizes S3 paths to avoid malformed keys

### Lambda Handler

```
app.lambdas.ingestion_lambdas.handler
```

## Part 2 – API Ingestion

### What it does

- Fetches population data from the DataUSA API
- Stores the response as timestamped JSON files in S3
- Uses the same ingestion Lambda via a dispatcher pattern

### Storage Layout

```
bls/
 ├── pr/          # BLS time-series data
 └── api/         # API JSON snapshots
```

**S3 Bucket:** [https://rearc-bls-data-sync-lambda.s3.us-east-1.amazonaws.com/](https://rearc-bls-data-sync-lambda.s3.us-east-1.amazonaws.com/)

## Part 3 – Analytics & Reporting

### Trigger Mechanism

- S3 ObjectCreated events → SQS
- SQS → Analytics Lambda

### Analytics Lambda Responsibilities

- Loads the latest API JSON from S3
- Loads the BLS time-series CSV from S3
- Executes analytical queries derived from the original notebook
- Logs report outputs to CloudWatch

### Reports Generated

1. Mean and standard deviation of U.S. population (2013–2018)
2. Best year per series_id (maximum annual value)
3. Joined report for series_id = PRS30006032, period = Q01, with population
> **Note:** No notebooks are executed in Lambda. Notebook logic was refactored into Python.

### Lambda Handler

```
app.lambdas.bls_reports_lambda.handler
```

### Lambda Layers

- Pandas is provided via an AWS-managed Lambda layer
- The layer is resolved dynamically in Terraform using a data source
- This avoids platform-specific binary issues and keeps deployment clean

Example:

```hcl
data "aws_lambda_layer_version" "sdk_pandas" {
  layer_name = "AWSSDKPandas-Python314"
}
```

> **Note:** The analytics Lambda uses Python 3.14 runtime with the AWSSDKPandas layer.

## Infrastructure as Code (Terraform)

All AWS resources are created using Terraform:

- S3 bucket
- SQS queue and queue policy
- IAM execution role and policies
- Ingestion Lambda
- Analytics Lambda
- S3 → SQS notifications
- SQS → Lambda event source mapping

### Terraform Structure

```
infra/terraform/
 ├── main.tf
 ├── variables.tf
 ├── iam.tf
 ├── s3.tf
 ├── sqs.tf
 ├── lambda.tf
 ├── analytics_lambda.tf
 └── outputs.tf
```

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform installed (>= 1.0)
- Python 3.x for local development
- PowerShell (for Windows build script)

## Deployment

### Step 1: Build Lambda Packages

First, build the Lambda deployment packages:

```powershell
.\build_lambda_packages.ps1
```

This will create:
- `bls_ingestion_lambda.zip`
- `analytics_consumer_lambda.zip`

### Step 2: Deploy Infrastructure

Navigate to the Terraform directory and initialize:

```bash
cd infra/terraform
terraform init
```

Deploy the infrastructure:

```bash
terraform apply \
  -var="bucket_name=rearc-bls-data-sync-lambda" \
  -var="lambda_zip_path=../../bls_ingestion_lambda.zip" \
  -var="analytics_lambda_zip_path=../../analytics_consumer_lambda.zip"
```

> **Note:** The S3 bucket name is `rearc-bls-data-sync-lambda`. If you need to use a different bucket name, update the `bucket_name` variable accordingly.

**S3 Bucket URL:** [https://rearc-bls-data-sync-lambda.s3.us-east-1.amazonaws.com/](https://rearc-bls-data-sync-lambda.s3.us-east-1.amazonaws.com/)

## Local Development & Testing

### Local Lambda Execution

Lambdas can be run locally using small runner scripts:

- AWS credentials are picked up from the local environment
- SQS events are simulated using the same JSON structure Lambda receives

Example:

```bash
# Set environment variables
export BLS_BUCKET=rearc-bls-data-sync-lambda
export BLS_BASE_URL=https://download.bls.gov
export BLS_PREFIX=bls/pr/

# Run analytics Lambda locally
python local_run.py
```

### Packaging

Lambda deployment artifacts are built locally using a reproducible script:

```powershell
.\build_lambda_packages.ps1
```

The script:
- Installs Python dependencies (requests, beautifulsoup4) for the ingestion Lambda
- Packages Lambda code with proper directory structure
- Creates deployment-ready ZIP files
- Cleans up temporary build directories

## Design Decisions

- **Terraform** chosen for clarity, portability, and reviewer friendliness
- **Single-responsibility Lambdas** for ingestion and analytics
- **Event-driven architecture** using S3 + SQS
- **No hard-coded filenames** - dynamic file discovery
- **No notebook execution in production** - logic refactored to Python
- **AWS-managed Lambda layers** for binary compatibility

## Security

- S3 bucket is private (no public access)
- IAM roles are scoped to required services
- SQS policies restrict access to the source S3 bucket
- Root user is used only for initial IAM bootstrapping

## Project Structure

```
rearc_data_quest/
├── app/
│   ├── lambdas/
│   │   ├── data_ingestion/
│   │   │   ├── ingestion_lambdas.py
│   │   │   ├── sync_bls_to_s3.py
│   │   │   └── fetch_api_to_s3.py
│   │   └── analytics/
│   │       └── bls_reports_lambda.py
│   └── notebooks/
│       └── data_analytics.ipynb
├── infra/
│   └── terraform/
│       ├── main.tf
│       ├── variables.tf
│       ├── iam.tf
│       ├── s3.tf
│       ├── sqs.tf
│       ├── lambda.tf
│       ├── analytics_lambda.tf
│       └── outputs.tf
├── build_lambda_packages.ps1
├── local_run.py
├── requirements.txt
└── README.md
```

## TODOs / Future Improvements

- **Testing**: Add unit tests and integration tests for ingestion and analytics Lambdas (including S3/SQS event simulations).
- **Retries & DLQ**: Configure SQS redrive policy and a dedicated dead-letter queue for failed analytics events; add explicit retry logic where appropriate.
- **Error Handling**: Harden error handling in Lambdas (graceful failures, clear log messages, and alerting hooks via CloudWatch Alarms).
- **Observability**: Add structured logging, metrics, and dashboards (CloudWatch Metrics/Logs Insights) for ingestion and analytics performance.
- **Configuration**: Externalize runtime configuration (e.g., prefixes, API URLs) via environment variables and/or SSM Parameter Store.
- **Security Hardening**: Review IAM policies for least privilege and consider KMS encryption for S3/SQS where needed.
- **Git Hygiene**: Add a `.gitignore` tuned for Python, Terraform, and build artifacts (e.g., `__pycache__/`, `.terraform/`, `*.zip`, virtualenvs).

## AI Assistance

- **README authoring**: AI was used to structure and refine this README, including architecture description, deployment instructions, and documentation of design decisions.
- **Terraform & AWS guidance**: AI helped suggest example Terraform snippets and AWS configuration patterns (e.g., Lambda layers, S3/SQS wiring).
- **Bugfixes & refactors**: AI assisted in debugging issues and refining implementation details to better match the intended architecture.
- **Template & structure generation**: AI was used to create project/file structure templates (e.g., Lambda layout, Terraform modules) which were then adapted and implemented.
- **Refinement & clarity**: AI assisted in rephrasing and organizing content to be reviewer-friendly while staying faithful to the implemented code. Prompts are not included here, as the interaction was an ongoing back-and-forth rather than a single static input.

## Summary

This solution demonstrates:

- ✅ Event-driven data ingestion
- ✅ Idempotent file synchronization
- ✅ Serverless analytics
- ✅ Infrastructure as Code
- ✅ Clean separation of concerns
- ✅ Production-aware AWS design decisions