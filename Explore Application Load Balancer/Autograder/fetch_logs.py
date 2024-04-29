import boto3
import json
import gzip
import shutil
import time
from multiprocessing import Process
import os

def fetch_logs(access_key_id, secret_access_key, region, bucket_name, prefix, client_ip):
    try:
        # Create a session using your credentials
        session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
    except Exception as e:
        print(f"Error creating session: {e}")
        return

    try:
        # Create an S3 client object using the session
        s3_client = session.client('s3')
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        return

    # Check if the bucket exists
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Bucket does not exist or you do not have access: {e}")
        return

    # Get the .log.gz files
    paginator = s3_client.get_paginator('list_objects_v2')

    try:
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    except Exception as e:
        print(f"Error paginating bucket: {e}")
        return

    for page in pages:
        # Check if the prefix is valid
        if not page['Contents']:
            print(f"No objects found with prefix '{prefix}'")
            return

        for obj in page['Contents']:
            if obj['Key'].endswith('.log.gz'):
                try:
                    # Download the .log.gz file
                    s3_client.download_file(bucket_name, obj['Key'], 'temp.log.gz')
                except Exception as e:
                    print(f"Error downloading file: {e}")
                    continue

                try:
                    # Extract the .log.gz file
                    with gzip.open('temp.log.gz', 'rb') as f_in:
                        with open('temp.log', 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                except Exception as e:
                    print(f"Error extracting file: {e}")
                    continue

                try:
                    # Append the contents of the .log file to access.log
                    with open('temp.log', 'r') as f_in:
                        log_data = f_in.read()
                        if client_ip in log_data:
                            with open('access.log', 'a') as f_out:
                                f_out.write(log_data)
                except Exception as e:
                    print(f"Error writing to 'access.log': {e}")

def main():
    # Delete temp.log, access.log, and temp.log.gz if they exist
    for filename in ['temp.log', 'access.log', 'temp.log.gz']:
        try:
            os.remove(filename)
        except OSError:
            pass

    try:
        # Load credentials from data.json
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File 'data.json' not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error decoding JSON from 'data.json'.")
        exit(1)

    access_key_id = data.get('INSTRUCTOR Access key ID')
    secret_access_key = data.get('INSTRUCTOR Secret Access Key')
    bucket_name = data.get('s3 bucket name')
    region = data.get('region')
    account = data.get('account-id')
    client_ip = data.get('client-ip')

    if not all([access_key_id, secret_access_key, bucket_name, region, account, client_ip]):
        print("Missing data in 'data.json'.")
        exit(1)

    # Define the prefix
    prefix = f'AWSLogs/{account}/elasticloadbalancing/'

    # Create a separate process for the log fetching operation
    p = Process(target=fetch_logs, args=(access_key_id, secret_access_key, region, bucket_name, prefix, client_ip))
    p.start()

    # Allow the log fetching operation to run for up to two minutes
    p.join(120)

    # If process is still running after two minutes, terminate it
    if p.is_alive():
        print("Two minutes have passed. Stopping log fetch.")
        p.terminate()
        p.join()

if __name__ == "__main__":
    main()
