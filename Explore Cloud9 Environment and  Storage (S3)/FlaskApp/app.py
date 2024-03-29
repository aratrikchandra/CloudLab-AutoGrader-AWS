from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
import boto3
import os
import uuid  # for generating unique IDs
from util import resize_image, allowed_file

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'Your_Secret_Key')

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'Your_Bucket_Name')

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
        file_path = os.path.join(app.root_path, unique_filename)
        file.save(file_path)

        # Check the file size
        if os.path.getsize(file_path) > MAX_IMAGE_SIZE:
            os.remove(file_path)  # remove the file if it's too large
            flash('File size exceeds maximum allowed size (2MB)', 'error')
            return redirect(request.url)

        try:
            # Resize the image
            resized_file_path = os.path.join(app.root_path, 'resized_' + unique_filename)
            resize_image(file_path, resized_file_path)

            # Upload to S3 with the unique filename
            s3.upload_file(
                Filename=resized_file_path,
                Bucket=BUCKET_NAME,
                Key=unique_filename
            )

            flash(f'File uploaded successfully.Image ID: {unique_filename}', 'success')

            os.remove(file_path)
            os.remove(resized_file_path)
        except Exception as e:
            os.remove(file_path)  # ensure the file is removed in case of an error
            os.remove(resized_file_path)
            flash(f'Error uploading file: {str(e)}', 'error')

        return redirect(request.url)

    return render_template('upload.html', allowed_extensions=ALLOWED_EXTENSIONS, max_size_mb=MAX_IMAGE_SIZE/(1024*1024))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
