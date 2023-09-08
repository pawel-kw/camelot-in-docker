import camelot
import re
import os
import yaml
import boto3
import botocore

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("AWS_S3_ENDPOINT_URL"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    config=boto3.session.Config(signature_version="s3v4"),
)


def _deconstruct_s3_url(url):
    return re.match("s3://([^/]+)/(.*)", url).groups()


def load_config(file_path):
    with open(file_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    return config


def list_objects(bucket, prefix=""):
    print(f"Calling list_objects with bucket: {bucket} and prefix: {prefix}")
    try:
        args = dict(Bucket=bucket)
        if prefix != "":
            args["Prefix"] = prefix
        return [o["Key"] for o in s3.list_objects_v2(**args).get("Contents", [])]
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            return []
        else:
            raise e


def main():
    # The function downloads all files in teh given s3 bucket. It assumes there should be a pdf and a yml with the
    # same name. The yml is expected to contain input parameters for camelot to extract the table.

    input_bucket, input_key = _deconstruct_s3_url(os.environ["INPUT"])
    output_bucket, output_dir = _deconstruct_s3_url(os.environ["OUTPUT"])
    output_dir = output_dir if output_dir.endswith("/") else output_dir + "/"

    # List objects in the input bucket and download them
    object_list = list_objects(input_bucket, input_key)
    config_files = []
    for object_key in object_list:
        input_dir = "/".join(input_key.split("/")[:-1])
        if input_dir and not os.path.exists(input_dir):
            os.makedirs(input_dir)
        s3.download_file(input_bucket, object_key, object_key)
        if ".yml" in object_key:
            config_files.append(object_key)

    # Check if there are any config files, return an error if the list is empty, continue with processing when
    # there are config files
    if len(config_files) == 0:
        print("No config files found")
        return
    else:
        print(f"Found {len(config_files)} config files")

    # Process each config file
    for config_file in config_files:
        with open(config_file, "r") as cf:
            config = yaml.safe_load(cf)
        read_pdf_options = config.get("read_pdf", {})
        pdf_file = config_file.replace(".yml", ".pdf")

        # Extract tables
        tables = camelot.read_pdf(
            pdf_file,
            **read_pdf_options,
        )

        # Write tables to CSV
        output_file = pdf_file.replace(".pdf", ".csv")
        tables_dir = os.path.join(input_dir + "tables")
        os.makedirs(tables_dir, exist_ok=True)
        tables.export(os.path.join(tables_dir, output_file), f="csv", compress=False)

        # Upload to output S3 bucket
        if output_dir == "/":
            output_dir = ""
        for subdir, dirs, files in os.walk(tables_dir):
            for file in files:
                if not file.endswith("json"):
                    s3.upload_file(
                        Filename=os.path.join(subdir, file),
                        Bucket=output_bucket,
                        Key=output_dir + file,
                        ExtraArgs=dict(
                            ContentType="text/csv",
                            ContentEncoding="gzip",
                            CacheControl="private,max-age=31536000",
                        ),
                    )


if __name__ == "__main__":
    main()
