from app.lambdas.sync_bls_to_s3 import handler as sync_handler
from app.lambdas.fetch_api_to_s3 import handler as api_handler

if __name__ == "__main__":
    # print("Running sync lambda locally")
    # print(sync_handler({}, None))

    print("Running API lambda locally")
    print(api_handler({}, None))
