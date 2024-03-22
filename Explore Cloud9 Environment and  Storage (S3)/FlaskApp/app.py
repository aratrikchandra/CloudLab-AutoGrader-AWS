from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
import boto3
import os
from util import resize_image, allowed_file

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

s3 = boto3.client('s3')
BUCKET_NAME = 'your-bucket-name'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            flash('Invalid file type. Only images are allowed.')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.root_path, filename)
        file.save(file_path)
        
        # Resize the image
        resized_file_path = os.path.join(app.root_path, 'resized_' + filename)
        resize_image(file_path, resized_file_path)

        # Upload to S3
        try:
            s3.upload_file(
                Filename=resized_file_path,
                Bucket=BUCKET_NAME,
                Key=filename
            )
            os.remove(file_path)
            os.remove(resized_file_path)
            flash('File uploaded successfully', 'success')
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'error')

        return redirect(request.url)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
