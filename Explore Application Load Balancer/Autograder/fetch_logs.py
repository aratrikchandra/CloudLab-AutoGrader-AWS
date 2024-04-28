import boto3
import json
import gzip
import shutil

# Load credentials from data.json
with open('data.json', 'r') as f:
    data = json.load(f)

access_key_id = data['INSTRUCTOR Access key ID']
secret_access_key = data['INSTRUCTOR Secret Access Key']
bucket_name = data['s3 bucket name']
region = data['region']
account = data['account-id']
client_ip = data['client-ip']
# Create a session using your credentials
session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name=region
)

# Create an S3 client object using the session
s3_client = session.client('s3')

# Define the prefix
prefix = f'AWSLogs/{account}/elasticloadbalancing/'

# Get the .log.gz files
paginator = s3_client.get_paginator('list_objects_v2')
for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
    for obj in page['Contents']:
        if obj['Key'].endswith('.log.gz'):
            # Download the .log.gz file
            s3_client.download_file(bucket_name, obj['Key'], 'temp.log.gz')
            # Extract the .log.gz file
            with gzip.open('temp.log.gz', 'rb') as f_in:
                with open('temp.log', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Append the contents of the .log file to access.log
            with open('temp.log', 'r') as f_in:
                log_data = f_in.read()
                if client_ip in log_data:
                    with open('access.log', 'a') as f_out:
                        f_out.write(log_data)
