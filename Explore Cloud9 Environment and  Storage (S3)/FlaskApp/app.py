from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import boto3
import os

app = Flask(__name__)

s3 = boto3.client('s3')

BUCKET_NAME = 'your-bucket-name'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(filename)
        s3.upload_file(
            Bucket = BUCKET_NAME,
            Filename=filename,
            Key = filename
        )
        os.remove(filename)  # remove the file from the application
        return redirect(url_for('upload_file'))

    return '''
    <!doctype html>
    <title>Upload a File</title>
    <h1>Upload a File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
