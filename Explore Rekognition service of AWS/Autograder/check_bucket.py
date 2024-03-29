import boto3
import json

# Initialize the score
score = 0

# Load the data.json file
try:
    with open('data.json') as f:
        data = json.load(f)
except FileNotFoundError:
    print("The file 'data.json' was not found.")
    exit(1)
except json.JSONDecodeError:
    print("There was an error decoding the JSON file.")
    exit(1)

# Extract the necessary information
try:
    access_key = data['INSTRUCTOR Access key ID']
    secret_key = data['INSTRUCTOR Secret Acess Key']
    bucket_name = data['s3 bucket name']
    uploaded_images = data['uploaded_images']
except KeyError as e:
    print(f"The key {e} was not found in the data.")
    exit(1)

# Create a session using the provided IAM user credentials
try:
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
except Exception as e:
    print(f"There was an error creating the session: {e}")
    exit(1)

# Create an S3 resource object using the above session
s3 = session.resource('s3')

# Function to check if bucket exists
def check_bucket_exists(bucket_name):
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
        return True
    except Exception as e:
        print(f"There was an error checking if the bucket exists: {e}")
        return False

# Function to check if an object exists in the bucket
def check_object_exists(bucket_name, object_name):
    try:
        s3.Object(bucket_name, object_name).load()
        return True
    except Exception as e:
        print(f"There was an error checking if the object exists: {e}")
        return False

# Check if the bucket exists
if check_bucket_exists(bucket_name):
    print(f'Bucket {bucket_name} exists.')
    score += 25
else:
    print(f'Bucket {bucket_name} does not exist.')
    print(f'Total score: {score}')
    exit(1)

# Check if the images exist in the bucket
for image in uploaded_images:
    if check_object_exists(bucket_name, image):
        print(f'Image {image} exists in the bucket.')
        score += 25
    else:
        print(f'Image {image} does not exist in the bucket.')

print(f'Total score: {score}')
