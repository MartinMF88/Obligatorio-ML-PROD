import boto3
import numpy as np
from PIL import Image
import io

# Bucket name and prefix (directory)
bucket_name = 'obligatoriomlprodmmmbfm'
prefix = 'images/'

# Create an S3 client
s3_client = boto3.client('s3')

# List objects in the bucket under the specified prefix
response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

# Filter image keys (assuming they are .jpg or .png)
image_keys = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith(('.jpg', '.png'))]

# Function to read an image from S3
def read_image_from_s3(bucket, key):
    s3_response_object = s3_client.get_object(Bucket=bucket, Key=key)
    object_content = s3_response_object['Body'].read()
    return Image.open(io.BytesIO(object_content))