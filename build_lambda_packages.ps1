# -----------------------------
# CONFIG
# -----------------------------
$INGESTION_ZIP = "bls_ingestion_lambda.zip"
$ANALYTICS_ZIP = "analytics_consumer_lambda.zip"

$INGESTION_BUILD = "lambda_build"
$ANALYTICS_BUILD = "analytics_lambda_build"

# -----------------------------
# CLEAN OLD BUILDS
# -----------------------------
Write-Host "Cleaning old build directories..."

Remove-Item -Recurse -Force $INGESTION_BUILD -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $ANALYTICS_BUILD -ErrorAction SilentlyContinue
Remove-Item $INGESTION_ZIP -ErrorAction SilentlyContinue
Remove-Item $ANALYTICS_ZIP -ErrorAction SilentlyContinue

# -----------------------------
# BUILD INGESTION LAMBDA
# -----------------------------
Write-Host "Building ingestion lambda..."

New-Item -ItemType Directory -Path $INGESTION_BUILD | Out-Null

pip install requests beautifulsoup4 -t $INGESTION_BUILD

Copy-Item app\lambdas\data_ingestion $INGESTION_BUILD\app\lambdas -Recurse

Push-Location $INGESTION_BUILD
Compress-Archive -Path * -DestinationPath "..\$INGESTION_ZIP"
Pop-Location

Write-Host "Created $INGESTION_ZIP"

# -----------------------------
# BUILD ANALYTICS LAMBDA
# -----------------------------
Write-Host "Building analytics lambda..."

New-Item -ItemType Directory -Path $ANALYTICS_BUILD | Out-Null

# Pandas is NOT included in Lambda by default
# pip install pandas -t $ANALYTICS_BUILD

Copy-Item app\lambdas\analytics $ANALYTICS_BUILD\app\lambdas -Recurse

Push-Location $ANALYTICS_BUILD
Compress-Archive -Path * -DestinationPath "..\$ANALYTICS_ZIP"
Pop-Location

Write-Host "Created $ANALYTICS_ZIP"

# -----------------------------
# VERIFY ZIP CONTENTS
# -----------------------------
Write-Host "`nVerifying ZIP contents..."

tar -tf $INGESTION_ZIP | Select-Object -First 10
tar -tf $ANALYTICS_ZIP | Select-Object -First 10

Write-Host "`nBuild completed successfully."
