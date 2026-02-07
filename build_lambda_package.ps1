# Define variables
$LAMBDA_DIR = "app/lambdas"
$TEMP_DIR = "lambda_build"
$ZIP_FILE = "lambda_package.zip"

# Remove old build directory and zip file if they exist
if (Test-Path $TEMP_DIR) {
    Remove-Item -Recurse -Force $TEMP_DIR
}

if (Test-Path $ZIP_FILE) {
    Remove-Item -Force $ZIP_FILE
}

# Create a temporary directory for the build
New-Item -ItemType Directory -Path $TEMP_DIR

# Create a subdirectory for the Lambda function code
$LAMBDA_SUBDIR = "$TEMP_DIR\app\lambdas"
New-Item -ItemType Directory -Path $LAMBDA_SUBDIR

# Install dependencies into the temporary directory
pip install -r requirements.txt -t $TEMP_DIR

# Copy the Lambda function code into the subdirectory
Copy-Item -Path "$LAMBDA_DIR\*" -Destination $LAMBDA_SUBDIR -Recurse

# Create a zip file for the deployment package
Compress-Archive -Path "$TEMP_DIR\\*" -DestinationPath $ZIP_FILE

# Clean up the temporary directory
Remove-Item -Recurse -Force $TEMP_DIR

Write-Host "Deployment package created: $ZIP_FILE"