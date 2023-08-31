import os
from main import main, list_objects
import boto3
import botocore

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("AWS_S3_ENDPOINT_URL"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    config=boto3.session.Config(signature_version="s3v4"),
)


def delete_objects(bucket, prefix=""):
    objects = list_objects(bucket, prefix)
    if objects:
        s3.delete_objects(
            Bucket=bucket, Delete=dict(Objects=[dict(Key=k) for k in objects])
        )


if __name__ == "__main__":
    delete_objects("output")
    os.environ["INPUT"] = "s3://input/"
    os.environ["OUTPUT"] = "s3://output/"
    main()
