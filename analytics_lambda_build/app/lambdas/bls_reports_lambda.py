import json
import logging
import os
from io import StringIO

import boto3
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

# Config
BUCKET = os.getenv("BLS_BUCKET")   # reuse same bucket
CSV_KEY = "bls/pr//pub/time.series/pr/pr.data.0.Current"
JSON_PREFIX = "bls/api/"


# -----------------------------
# S3 LOAD HELPERS
# -----------------------------

def load_s3_csv(bucket, key):
    print(f"Loading CSV from s3://{bucket}/{key}")
    obj = s3.get_object(Bucket=bucket, Key=key)
    raw = obj["Body"].read().decode("utf-8")

    df = pd.read_csv(StringIO(raw), sep="\t")

    # Cleaning (from notebook)
    df.columns = df.columns.str.strip().str.lower()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(how="all")
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    return df


def load_latest_json(bucket, prefix):
    paginator = s3.get_paginator("list_objects_v2")

    latest_key = None
    latest_ts = None

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if latest_ts is None or obj["LastModified"] > latest_ts:
                latest_key = obj["Key"]
                latest_ts = obj["LastModified"]

    if not latest_key:
        raise RuntimeError("No JSON files found under prefix")

    logger.info("Latest JSON key: %s", latest_key)

    obj = s3.get_object(Bucket=bucket, Key=latest_key)
    payload = json.loads(obj["Body"].read().decode("utf-8"))

    return pd.DataFrame(payload["data"])


# -----------------------------
# REPORTS (FROM NOTEBOOK)
# -----------------------------

def population_stats(df_json, start=2013, end=2018):
    df = df_json[
        (df_json["Year"] >= start) &
        (df_json["Year"] <= end)
    ]

    return {
        "years": f"{start}-{end}",
        "mean_population": df["Population"].mean(),
        "std_population": df["Population"].std(),
    }


def best_year_per_series(df_csv):
    grouped = (
        df_csv
        .groupby(["series_id", "year"])["value"]
        .sum()
        .reset_index()
    )

    best = grouped.loc[
        grouped.groupby("series_id")["value"].idxmax()
    ]

    return best.rename(
        columns={"year": "best_year", "value": "max_value"}
    )


def q1_population_report(df_csv, df_json):
    filtered = df_csv[
        (df_csv["series_id"] == "PRS30006032") &
        (df_csv["period"] == "Q01")
    ]

    report = filtered.merge(
        df_json[["Year", "Population"]],
        left_on="year",
        right_on="Year",
        how="left"
    )

    return report[["series_id", "year", "period", "value", "Population"]]


# -----------------------------
# LAMBDA ENTRYPOINT (SQS)
# -----------------------------

def handler(event, context):
    logger.info("Analytics consumer triggered")
    logger.info("Received %d SQS message(s)", len(event.get("Records", [])))

    # Load datasets once per invocation
    df_csv = load_s3_csv(BUCKET, CSV_KEY)
    df_json = load_latest_json(BUCKET, JSON_PREFIX)

    # ---- Report 1 ----
    stats = population_stats(df_json)
    logger.info("REPORT 1: Population statistics (2013–2018)")
    logger.info(stats)

    # ---- Report 2 ----
    best_years = best_year_per_series(df_csv)
    logger.info("REPORT 2: Best year per series (sample 10 rows)")
    logger.info(best_years.head(10).to_string(index=False))

    # ---- Report 3 ----
    q1_report = q1_population_report(df_csv, df_json)
    logger.info("REPORT 3: Q01 + Population report")
    logger.info(q1_report.to_string(index=False))

    return {
        "status": "reports_generated",
        "records_processed": len(event.get("Records", []))
    }
