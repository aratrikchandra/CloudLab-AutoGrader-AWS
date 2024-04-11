import boto3
import json
import os

s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')

# Retrieve the labels bucket name from environment variables
LABELS_BUCKET = os.environ.get('LABELS_BUCKET', 'Your_Labels_Bucket_Name')

def lambda_handler(event, context):
    # Get the bucket name and key (file name) from the event triggered by S3
    source_bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_key = event['Records'][0]['s3']['object']['key']
    
    # Use Amazon Rekognition to detect labels in the image
    try:
        response = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': source_bucket_name,
                    'Name': image_key
                }
            },
            MaxLabels=10
        )

        # Extract labels from the Rekognition response
        labels = [label['Name'] for label in response['Labels']]
        
        # Construct the record to be saved. This record links the image name to its labels.
        record = {
            'Image': image_key,
            'Labels': labels
        }
        
        # Store the labels in the labels bucket
        labels_key = f'labels/{image_key}.json'
        s3_client.put_object(
            Bucket=LABELS_BUCKET,
            Key=labels_key,
            Body=json.dumps(record)
        )

        return {
            'statusCode': 200,
            'body': json.dumps('Labels processed and saved successfully.')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing labels: {str(e)}')
        }
