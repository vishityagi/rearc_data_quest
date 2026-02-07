from app.lambdas.sync_bls_to_s3 import handler as bls_handler
from app.lambdas.fetch_api_to_s3 import handler as api_handler

def handler(event, context):
    job = event.get("job", "bls_sync")

    if job == "bls_sync":
        return bls_handler(event, context)

    if job == "api_fetch":
        return api_handler(event, context)

    if job == "all":
        bls_result = bls_handler(event, context)
        api_result = api_handler(event, context)

        return {
            "job": "all",
            "bls_sync": bls_result,
            "api_fetch": api_result
        }

    raise ValueError(f"Unknown job: {job}")
