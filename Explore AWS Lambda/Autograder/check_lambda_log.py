import boto3
import json
import os

def check_lambda_trigger(log_group_name, filter_pattern):
    client = boto3.client('logs')
    response = client.filter_log_events(
        logGroupName=log_group_name,
        filterPattern=filter_pattern
    )
    
    events = response['events']
    
    while 'nextToken' in response:
        response = client.filter_log_events(
            logGroupName=log_group_name,
            filterPattern=filter_pattern,
            nextToken=response['nextToken']
        )
        events.extend(response['events'])
    
    return events


# Load student data
with open('data.json') as f:
    data = json.load(f)

# Load fetch.json
with open('fetch.json') as f:
    fetch_data = json.load(f)

# Set AWS credentials
os.environ['AWS_ACCESS_KEY_ID'] = data['INSTRUCTOR Access key ID']
os.environ['AWS_SECRET_ACCESS_KEY'] = data['INSTRUCTOR Secret Acess Key']
os.environ['AWS_DEFAULT_REGION'] = data['region']

# Set log group name
log_group_name = f'/aws/lambda/{data["Lambda Function Name"]}'  # replace with your Lambda function name

# Fetch all logs
all_events = check_lambda_trigger(log_group_name, '')

# Save log messages to a text file
with open('lambda_logs.txt', 'w') as f:
    for event in all_events:
        f.write(event['message'] + '\n')

# Load log messages from file
with open('lambda_logs.txt', 'r') as f:
    log_lines = f.read().splitlines()

# Perform log checks
for image, expected_labels in fetch_data.items():
    # Check if logs contain processing image message
    processing_message = f'Processing image: {image} from bucket: {data["source s3 bucket name"]}'
    if any(processing_message in log_msg for log_msg in log_lines):
        print(f'Initial log found for image: {image}')
    else:
        print(f'Initial log not found for image: {image}')
        continue

    # Check if logs contain generated labels message
    generated_labels_message = f'Generated labels for image: {image}'
    if any(generated_labels_message in log_msg for log_msg in log_lines):
        print(f'Generated labels log found for image: {image}')
    else:
        print(f'Generated labels log not found for image: {image}')
        continue

    # Check if logs contain successful processing message
    success_message = f'Successfully processed labels for image: {image} and stored in bucket: {data["labels s3 bucket name"]}'
    if any(success_message in log_msg for log_msg in log_lines):
        print(f'Successful processing log found for image: {image}')
    else:
        print(f'Successful processing log not found for image: {image}')
