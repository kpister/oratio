import os
from google.cloud import storage

from constants.constants import (
    REPO_PATH,
    GCLOUD_UPLOAD_BUCKET_NAME,
)


# Will first check for keyfile credentials, then use the gcloud utility.
# returns None on failure
def get_client():
    print("Using GCloud for storage client")
    error = []
    try:
        client = storage.Client.from_service_account_json(
            os.path.join(REPO_PATH, ".keyfile.json")
        )
        return client
    except Exception as e:
        error.append(str(e))

    try:
        return storage.Client()
    except Exception as e:
        error.append(str(e))

    print("\n".join(error))
    return None


# input_file is a complete path
def upload_file_to_cloud(storage_client, input_file, upload_name):
    bucket = storage_client.bucket(GCLOUD_UPLOAD_BUCKET_NAME)
    blob = bucket.blob(upload_name)
    blob.upload_from_filename(input_file)

    blob.make_public()
    print(f"Blob {blob.name} is publicly accessible at {blob.public_url}")
