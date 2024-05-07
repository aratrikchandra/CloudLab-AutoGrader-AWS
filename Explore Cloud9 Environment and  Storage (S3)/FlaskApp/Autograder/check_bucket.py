import boto3
import json
import cv2
from botocore.exceptions import NoCredentialsError, ClientError

# Load the data.json file
try:
    with open('data.json') as f:
        data = json.load(f)
except FileNotFoundError:
    print("The file 'data.json' was not found.")
    exit(1)

# Extract the necessary information
try:
    access_key = data['INSTRUCTOR Access key ID']
    secret_key = data['INSTRUCTOR Secret Access Key']
    bucket_name = data['s3 bucket name']
    input_image_name = data['Input Image Name']
    uploaded_image_name = data['Uploaded Image Name']
    region = data['Region']
except KeyError as e:
    print(f"The key {e} was not found in the data.")
    exit(1)

# Create a session using the provided IAM user credentials
try:
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
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
    except ClientError:
        return False

# Check if the bucket exists
if not check_bucket_exists(bucket_name):
    print(f'Bucket {bucket_name} does not exist.')
    exit(1)

# Function to download an object from the bucket
def download_object(bucket_name, object_name, file_name):
    try:
        s3.Bucket(bucket_name).download_file(object_name, file_name)
        return True
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except ClientError:
        print(f"Object {object_name} does not exist in the bucket.")
        return False

# Download the uploaded image
if not download_object(bucket_name, uploaded_image_name, 'test_images/uploaded_image.jpg'):
    print(f'Image {uploaded_image_name} could not be downloaded from the bucket.')
    exit(1)

# Load the input image and the downloaded image
input_image = cv2.imread(input_image_name)
uploaded_image = cv2.imread('test_images/uploaded_image.jpg')

# Resize the input image to match the size of the uploaded image
resized_input_image = cv2.resize(input_image, (uploaded_image.shape[1], uploaded_image.shape[0]))

# Calculate the histograms of the images
hist_input_image = cv2.calcHist([resized_input_image], [0], None, [256], [0,256])
hist_uploaded_image = cv2.calcHist([uploaded_image], [0], None, [256], [0,256])

# Normalize the histograms
hist_input_image = cv2.normalize(hist_input_image, hist_input_image)
hist_uploaded_image = cv2.normalize(hist_uploaded_image, hist_uploaded_image)

# Compare the histograms
comparison = cv2.compareHist(hist_input_image, hist_uploaded_image, cv2.HISTCMP_CORREL)
# print(comparison)
if comparison >= 0.9:
    print("The input image and the uploaded image are same.")
else:
    print("The input image and the uploaded image are not same.")
