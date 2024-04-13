import boto3
import json

# Load credentials and settings from data.json
try:
    with open('data.json') as f:
        data = json.load(f)
except FileNotFoundError:
    print("data.json file not found.")
    exit(1)

# Create a session using the credentials from data.json
try:
    session = boto3.Session(
        aws_access_key_id=data['INSTRUCTOR Access key ID'],
        aws_secret_access_key=data['INSTRUCTOR Secret Acess Key'],
        region_name=data['region']
    )
except Exception as e:
    print("Failed to create a session. Check your IAM credentials.")
    exit(1)

# Create S3 resource object
s3 = session.resource('s3')

# Load the image names and labels from fetch.json
try:
    with open('fetch.json') as f:
        fetch_data = json.load(f)
except FileNotFoundError:
    print("fetch.json file not found.")
    exit(1)

# Iterate over each image and its labels
for image, labels in fetch_data.items():
    # Check if image exists in source S3 bucket
    try:
        photo_object=s3.Object(data['source s3 bucket name'], image).get()
    except s3.meta.client.exceptions.NoSuchBucket as e:
        print(f"Bucket {data['source s3 bucket name']} does not exist.")
        continue
    except s3.meta.client.exceptions.NoSuchKey as e:
        print(f"Image {image} does not exist in source S3 bucket.")
        continue
    except Exception as e:
        print(f"An error occurred while checking the image {image} in the source S3 bucket: {str(e)}")
        continue

    # Check if labels exist in labels S3 bucket
    try:
        labels_object = s3.Object(data['labels s3 bucket name'], f"labels/{image}.json").get()
        stored_labels = json.loads(labels_object['Body'].read().decode())['Labels']

        # Check if the labels match
        if set(labels) != set(stored_labels):
            print(f"Labels for {image} do not match.")
        else:
            print(f"Labels for {image} match successfully.")
    except s3.meta.client.exceptions.NoSuchBucket as e:
        print(f"Bucket {data['labels s3 bucket name']} does not exist.")
    except s3.meta.client.exceptions.NoSuchKey as e:
        print(f"Labels for {image} do not exist in labels S3 bucket.")
    except Exception as e:
        print(f"An error occurred while checking the labels for {image} in the labels S3 bucket: {str(e)}")
