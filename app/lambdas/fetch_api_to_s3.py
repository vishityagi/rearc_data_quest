import os
import json
import boto3
import requests
from datetime import datetime

BUCKET = os.getenv("BLS_BUCKET")   # reuse same bucket

URL = "https://honolulu-api.datausa.io/tesseract/data.jsonrecords"

PARAMS = {
    "cube": "acs_yg_total_population_1",
    "drilldowns": "Year,Nation",
    "measures": "Population",
    "locale": "en"
}

HEADERS = {
    "User-Agent": "data-ingestion-assignment/1.0 (contact: your-email@example.com)",
    "Accept": "application/json"
}

s3 = boto3.client("s3")


# def handler(event=None, context=None):
#     r = requests.get(URL, params=PARAMS, headers=HEADERS, timeout=30)
#     r.raise_for_status()

#     payload = r.json()

#     # Generate a timestamped key
#     current_time = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
#     timestamped_key = f"bls/api/acs_population_{current_time}.json"

#     s3.put_object(
#         Bucket=BUCKET,
#         Key=timestamped_key,
#         Body=json.dumps(payload),
#         ContentType="application/json"
#     )

#     return {
#         "status": "success",
#         "records": len(payload.get("data", []))
#     }

# if __name__ == "__main__":
#     print(handler())

def handler(event=None, context=None):
    r = requests.get(URL, params=PARAMS, headers=HEADERS, timeout=30)
    r.raise_for_status()

    payload = r.json()

    mode = event.get("mode", "latest") if event else "latest"

    if mode == "history":
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        key = f"bls/api/acs_population_{ts}.json"
    else:
        key = "bls/api/acs_population_latest.json"

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(payload),
        ContentType="application/json"
    )

    return {
        "job": "api_fetch",
        "mode": mode,
        "records": len(payload.get("data", []))
    }

