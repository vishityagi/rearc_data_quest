# Part 1 logic + lambda handler
import os
import boto3
import requests
from bs4 import BeautifulSoup
import botocore

BUCKET = os.getenv("BLS_BUCKET")
PREFIX = os.getenv("BLS_PREFIX", "bls/pr")
BASE_URL = os.getenv("BLS_BASE_URL")
TIMEOUT = 30

s3 = boto3.client("s3")

# Add headers for requests
HEADERS = {
    "User-Agent": "rearc-dq-vidushi-bls-data-ingestion/1.0 (contact: vidushityagi.de@gmail.com)",
    "Content-Type": "application/json"
}


def handler(event=None, context=None):
    # Allow override from event (optional, future-proof)
    page_to_parse = (
        event.get("page", "/pub/time.series/pr")
        if event else "/pub/time.series/pr"
    )

    remote_files = list_remote_files(page=page_to_parse)
    s3_files = list_s3_files()

    print(f"Remote files: {remote_files}")
    print(f"S3 files: {s3_files}")

    uploaded = 0
    for f in remote_files:
        if upload_if_needed(f):
            uploaded += 1

    deleted = s3_files - remote_files
    for f in deleted:
        s3.delete_object(
            Bucket=BUCKET,
            Key=f"{PREFIX}{f}"
        )

    return {
        "job": "bls_sync",
        "uploaded": uploaded,
        "deleted": len(deleted)
    }



def list_remote_files(page):
    r = requests.get(BASE_URL + page, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    return {
        a.get("href")
        for a in soup.find_all("a")
        if a.get("href") and not a.get("href").endswith("/")
    }


def list_s3_files():
    paginator = s3.get_paginator("list_objects_v2")
    files = set()

    for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
        for obj in page.get("Contents", []):
            files.add(obj["Key"].replace(PREFIX, ""))

    return files


def remote_signature(filename):
    r = requests.head(BASE_URL + filename, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return (
        int(r.headers.get("Content-Length", 0)),
        r.headers.get("Last-Modified", "")
    )


def s3_signature(filename):
    # Debugging: Log bucket, prefix, and filename
    print(f"Checking S3 object: Bucket={BUCKET}, Key={PREFIX}{filename}")

    # Update exception handling to catch 404 errors
    try:
        obj = s3.head_object(
            Bucket=BUCKET,
            Key=f"{PREFIX}{filename}"
        )
        return (
            obj["ContentLength"],
            obj["Metadata"].get("source_last_modified", "")
        )
    except s3.exceptions.NoSuchKey:
        return None
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Object not found: {PREFIX}{filename}")
            return None
        else:
            raise


def upload_if_needed(filename):
    remote_sig = remote_signature(filename)
    s3_sig = s3_signature(filename)

    if s3_sig == remote_sig:
        return False

    data = requests.get(BASE_URL + filename, headers=HEADERS, timeout=TIMEOUT).content
    s3.put_object(
        Bucket=BUCKET,
        Key=f"{PREFIX}{filename}",
        Body=data,
        Metadata={"source_last_modified": remote_sig[1]}
    )
    return True
