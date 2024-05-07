import json
import boto3

# Load the data.json file
with open('data.json', 'r') as f:
    data = json.load(f)

# Create a session using your AWS credentials
session = boto3.Session(
    aws_access_key_id=data['INSTRUCTOR Access key ID'],
    aws_secret_access_key=data['INSTRUCTOR Secret Access Key'],
    region_name=data['Region']
)

# Create a CloudTrail client
client = session.client('cloudtrail')

# Fetch the event with the given Event ID
response = client.lookup_events(
    LookupAttributes=[
        {
            'AttributeKey': 'EventId',
            'AttributeValue': data['eventID']
        },
    ],
)

# Check if any events were returned
if response['Events']:
    # Get the first event (there should only be one with the same Event ID)
    event = response['Events'][0]
    # Parse the CloudTrail log
    cloudtrail_log = json.loads(event['CloudTrailEvent'])
    with open('access.json', 'w') as f_out:
    # Write the dictionary directly to a file in JSON format
        json.dump(cloudtrail_log, f_out, indent=4) 
                            

    # Check if all details match
    if (cloudtrail_log['userIdentity']['userName'] == data['userName'] and
        cloudtrail_log['requestParameters']['image']['s3Object']['bucket'] == data['s3 bucket name'] and
        cloudtrail_log['requestParameters']['image']['s3Object']['name'] == data['Uploaded Image Name'] and
        cloudtrail_log['eventID'] == data['eventID'] and
        cloudtrail_log['eventSource'] == data['eventSource'] and
        cloudtrail_log['eventName'] == data['eventName'] and
        cloudtrail_log['sourceIPAddress'] == data['public_ip']):
        print(f'Rekognition API was actually called for image: {data["Uploaded Image Name"]}')
    else:
        print(f'Rekognition API was not called for image: {data["Uploaded Image Name"]}')
else:
    print('No events found with the given Event ID')
