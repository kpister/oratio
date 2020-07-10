import boto3
from constants.constants import AWS_UPLOAD_BUCKET_NAME


def get_client():
    print("Using AWS for storage client")
    return boto3.client("s3")


# file_name is a complete path
def upload_file_to_cloud(client, file_name, upload_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param upload_name: The name of the file in the cloud
    """
    # Upload the file
    response = client.upload_file(file_name, AWS_UPLOAD_BUCKET_NAME, upload_name)
