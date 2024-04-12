import boto3
import json
import os
import logging

s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Retrieve the labels bucket name from environment variables
LABELS_BUCKET = os.environ.get('LABELS_BUCKET', 'Your_Labels_Bucket_Name')

def lambda_handler(event, context):
    # Get the bucket name and key (file name) from the event triggered by S3
    source_bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_key = event['Records'][0]['s3']['object']['key']
    
    logger.info(f'Processing image: {image_key} from bucket: {source_bucket_name}')  # Log the name of the image and the bucket

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
        
        # Log the generated labels
        logger.info(f'Generated labels for image: {image_key} are {labels}')
        
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

        logger.info(f'Successfully processed labels for image: {image_key} and stored in bucket: {LABELS_BUCKET}')  # Log success message

        return {
            'statusCode': 200,
            'body': json.dumps('Labels processed and saved successfully.')
        }
    except Exception as e:
        logger.error(f'Error processing labels for image: {image_key}, Error: {str(e)}')  # Log error message
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing labels: {str(e)}')
        }
