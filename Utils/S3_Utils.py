import io
import boto3
from botocore.exceptions import NoCredentialsError
import os
import sys

# Import environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')

# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def PIL_to_Buffer_S3(img):
    """
    Function to convert a PIL image to a buffer object

    Using JPEG format and 70% quality

    This is different from PIL_to_Buffer in that use PNG format
    """
    # Save the PIL image to a file-like object
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG',quality=70)

    # Get the bytes data from the buffer
    buf_data = buffer.getvalue()

    # Create a new BytesIO object with the same data
    new_buf = io.BytesIO(buf_data)

    # Create an _io.BufferedReader object from the new buffer
    buf_reader = io.BufferedReader(new_buf)

    return buf_reader

def upload_file_to_s3(image, file_name):

    # Convert image to buffer
    buffer = PIL_to_Buffer_S3(image)

    # Try to upload the file to S3
    try:
        s3.upload_fileobj(buffer, S3_BUCKET, file_name)
        print("S3 Upload Successful", file=sys.stderr)
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")