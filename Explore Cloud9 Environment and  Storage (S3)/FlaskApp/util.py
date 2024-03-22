from PIL import Image
import os


def resize_image(input_path, output_path, size=(300, 300)):
    """
    Resize the input image and save it to the output path.
    """
    with Image.open(input_path) as img:
        img.thumbnail(size)
        img.save(output_path)


def allowed_file(filename, allowed_extensions):
    """
    Check if the filename has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
