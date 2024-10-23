import boto3
import os
import requests
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_REGION')

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION_NAME
)

def upload_to_s3(file_data, file_name, folder=''):
    """
    Upload a file to the specified S3 bucket.
    
    :param file_data: Byte data of the file to upload
    :param file_name: Name of the file to save
    :param folder: (Optional) Folder in the bucket to upload the file to
    :return: URL of the uploaded file
    """
    try:
        s3_path = f"{file_name}.png" if folder else file_name
        s3.upload_fileobj(
            BytesIO(file_data),
            AWS_STORAGE_BUCKET_NAME,
            s3_path,
            ExtraArgs={'ACL': 'public-read'}
        )
        s3_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{s3_path}"
        return s3_url
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return None

def upload_image_to_s3(image_url, folder='images'):
    """
    Upload an image to S3 by URL.
    
    :param image_url: URL of the image to upload
    :param folder: Folder in S3 to upload the images to (default 'images')
    :return: URL of the uploaded image
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = response.content
        file_name = os.path.basename(image_url)
        return upload_to_s3(image_data, file_name, folder=folder)
    except Exception as e:
        print(f"Error uploading image to S3: {e}")
        return None

def upload_video_to_s3(video_url, folder='videos'):
    """
    Upload a video to S3 by URL.
    
    :param video_url: URL of the video to upload
    :param folder: Folder in S3 to upload the videos to (default 'videos')
    :return: URL of the uploaded video
    """
    try:
        response = requests.get(video_url)
        response.raise_for_status()
        video_data = response.content
        file_name = os.path.basename(video_url)
        return upload_to_s3(video_data, file_name, folder=folder)
    except Exception as e:
        print(f"Error uploading video to S3: {e}")
        return None

