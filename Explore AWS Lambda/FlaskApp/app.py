from flask import Flask, request, redirect, url_for, render_template, flash, session
from werkzeug.utils import secure_filename
import boto3
import os
import uuid  # for generating unique IDs
import json
from util import resize_image, allowed_file

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'Your_Secret_Key')

s3 = boto3.client('s3')

BUCKET_NAME = os.environ.get('BUCKET_NAME', 'Your_Bucket_Name')
LABELS_BUCKET = os.environ.get('LABELS_BUCKET', 'Your_Labels_Bucket_Name')

# print("The photo storage bucket name is: "+BUCKET_NAME)
# print("The labels storage bucket name is: "+LABELS_BUCKET)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            flash('Invalid file type. Only images are allowed.', 'error')
            return redirect(request.url)

        # Generate unique filename
        unique_filename = 'pic_' + str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()

        try:
            # Save the file temporarily
            file_path = os.path.join(app.root_path, unique_filename)
            file.save(file_path)

            # Check the file size
            if os.path.getsize(file_path) > MAX_IMAGE_SIZE:
                flash('File size exceeds maximum allowed size (2MB)', 'error')
                return redirect(request.url)

            # Resize the image
            resized_file_path = os.path.join(app.root_path, 'resized_' + unique_filename)
            resize_image(file_path, resized_file_path)

            # Upload to S3
            s3.upload_file(
                Filename=resized_file_path,
                Bucket=BUCKET_NAME,
                Key=unique_filename
            )

            flash('File uploaded successfully. Please wait a few moments for processing.', 'success')

            # Set session variable to indicate successful upload
            session['uploaded_image'] = unique_filename

        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'error')
        finally:
            # Cleanup: Remove temporary files
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(resized_file_path):
                os.remove(resized_file_path)

        return redirect(request.url)

    return render_template('upload.html', allowed_extensions=ALLOWED_EXTENSIONS, max_size_mb=MAX_IMAGE_SIZE/(1024*1024))

@app.route('/check_labels', methods=['POST'])
def check_labels():
    uploaded_image = session.get('uploaded_image')
    if uploaded_image:
        data = retrieve_labels(uploaded_image)
        if data:
            response = render_template('labels.html', data=data, uploaded_image=uploaded_image)
            # Clear the session variable after use
            session.pop('uploaded_image', None)
            return response
        else:
            flash('Labels not available for the uploaded image.', 'error')
            # Clear the session variable if no labels found
            session.pop('uploaded_image', None)
            return redirect(url_for('upload_file'))
    else:
        flash('Please upload a photo before checking labels.', 'error')
        return redirect(url_for('upload_file'))



def retrieve_labels(image_name):
    # Retrieve labels for the given image name from the labels bucket
    try:
        response = s3.get_object(Bucket=LABELS_BUCKET, Key=f'labels/{image_name}.json')
        data = json.loads(response['Body'].read())
        return data  # Return the entire data structure
    except Exception as e:
        print(f'Error retrieving labels for {image_name}: {str(e)}')
        return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
