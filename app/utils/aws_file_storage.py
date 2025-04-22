#!/usr/bin/env python3

""" Module for handling file upload to aws s3 bucket """
import boto3, os, time

from fastapi import UploadFile

# Configure AWS credentials
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
max_retries = os.getenv("FILE_UPLOAD_MAX_RETRIES")
retry_delay = os.getenv("FILE_UPLOAD_RETRY_DELAY")

# Create an S3 client
# s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

def upload_file_to_cloud(file: UploadFile, bucket_name: str, object_name: str, content_type) -> bool:
    """
    Uploads a file to AWS S3 bucket with retry mechanism
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Create an S3 client
            s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

            # Upload the file
            s3.upload_fileobj(file, bucket_name, object_name, ExtraArgs={'ContentType': content_type})

            print(f"File '{file}' uploaded to '{bucket_name}' as '{object_name}' on attempt {attempt}")
            return True
        except Exception as e:
            print(f"Error uploading file on Uattempt {attempt}: {str(e)}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    print(f"Max retry attempts reached. File upload failed.")
    return False

def get_file_from_cloud(file: str, dest:str, bucket_name: str, object_name: str) -> bool:
    """
    Retrieves a file to AWS S3 bucket with retry mechanism
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Create an S3 client
            s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key) 

            # download the file
            s3.download_file(bucket_name, object_name, dest)
 
            print(f"File '{file}' retrieved from '{bucket_name}' as '{dest}' on attempt {attempt}")
            return True
        except Exception as e:
            print(f"Error retrieving file on attempt {attempt}: {str(e)}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    print(f"Max retry attempts reached. File download failed.")
    return False