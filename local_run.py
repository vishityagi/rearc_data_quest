from app.lambdas.data_ingestion.sync_bls_to_s3 import handler as sync_handler
from app.lambdas.data_ingestion.fetch_api_to_s3 import handler as api_handler


# from app.lambdas.ingestion_lambdas import handler

# handler({"job": "bls_sync"}, None)
# handler({"job": "api_fetch"}, None)

import json
from app.lambdas.analytics.bls_reports_lambda import handler

# Simulate SQS event (same structure Lambda receives)
event = {
    "Records": [
        {
            "body": json.dumps({
                "Records": [
                    {
                        "s3": {
                            "bucket": {
                                "name": "rearc-bls-data-sync-lambda"
                            },
                            "object": {
                                "key": "bls/api/acs_population_20260207T201824Z.json"
                            }
                        }
                    }
                ]
            })
        }
    ]
}

if __name__ == "__main__":
    result = handler(event, context=None)
    print("Lambda result:")
    print(result)

