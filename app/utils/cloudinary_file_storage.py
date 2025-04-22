#!/usr/bin/env python3

""" Module for handling file upload to Cloudinary """
import os, time
import random
import string
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api

from fastapi import UploadFile
from dotenv import load_dotenv
from typing import List


from app.dependencies.error import httpError

# Load the environment variables from the .env file
load_dotenv()

# Configure Cloudinary credentials
cloudinary.config(
  cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
  api_key=os.getenv("CLOUDINARY_API_KEY"),
  api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

max_retries = int(os.getenv("FILE_UPLOAD_MAX_RETRIES"))
retry_delay = int(os.getenv("FILE_UPLOAD_RETRY_DELAY"))

async def upload_file_to_cloud(filename: str, file_content: bytes, public_id: str, folder: str, resource_type: str = "auto") -> dict:
    """
    Uploads a file to Cloudinary with retry mechanism
    """
    print(f"Uploading file '{filename}' to Cloudinary...")
    for attempt in range(1, max_retries + 1):
        try:
            # Upload the file
            response = cloudinary.uploader.upload(
                file_content,
                public_id=public_id,
                folder=folder,
                resource_type=resource_type
            )

            print(f"File '{filename}' uploaded to Cloudinary on attempt {attempt}")
            return {"success": True, "response": response}
        except Exception as e:
            print(f"Error uploading file on attempt {attempt}: {str(e)}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    print(f"Max retry attempts reached. File upload failed.")
    return {"success": False, "response": "Max retry attempts reached. File upload failed."}

async def process_file_upload(files: List[UploadFile], folder: str) -> dict:
    output = {"image_urls": [], "video_url": ""}

    for file in files:
        # Get file contents
        contents = await file.read()

        # Determine file extension
        file_extension = file.filename.split(".")[-1].lower()

        # Define content type based on file extension
        content_type = 'image' if file_extension in ['jpg', 'jpeg'] else 'video' if file_extension == 'mp4' else None

        # change spaces to underscores in filename
        file.filename = file.filename.replace(" ", "_")

        # Generate unique public id for the file like a filename from random unique string and filename
        public_id = f"{''.join(random.choices(string.ascii_lowercase, k=7))}-{file.filename.split('.')[0]}"

        # Call the function to upload the file
        response = await upload_file_to_cloud(file.filename, contents, public_id, folder, content_type)
        if not response["success"]:
            raise httpError(status_code=500, detail="Error uploading file to cloud storage")

        url = response["response"]["secure_url"]

        if file_extension == 'mp4':
            if output["video_url"] == '': # Checks if this is the first and only video to be uploaded for the project
                output["video_url"] = url
            else: # Throw error if a video has been stored previously
                raise httpError(status_code=400, detail="You cannot upload more than one video")
        elif file_extension in ['jpg', 'jpeg']:
            output["image_urls"].append(url)
    return output

def delete_file_from_cloud(public_id: str, resource_type: str = "image") -> bool:
    """
    Deletes a file from Cloudinary with retry mechanism
    """
    print(f"Deleting file '{public_id}' from Cloudinary...")
    for attempt in range(1, max_retries + 1):
        try:
            # Delete the file
            response = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            print(response)
            if response.get('result') == 'ok':
                print(f"File '{public_id}' deleted from Cloudinary on attempt {attempt}")
                return True
            else:
                raise Exception("File deletion failed")
        except Exception as e:
            print(f"Error deleting file on attempt {attempt}: {str(e)}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    print(f"Max retry attempts reached. File deletion failed.")
    return False

def get_file_from_cloud(public_id: str, dest: str, resource_type: str = "auto") -> bool:
    """
    Retrieves a file from Cloudinary with retry mechanism
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Get the file URL
            result = cloudinary.api.resource(public_id, resource_type=resource_type)
            file_url = result.get('url')

            if file_url:
                # Download the file
                with open(dest, 'wb') as file:
                    response = requests.get(file_url)
                    file.write(response.content)

                print(f"File '{public_id}' retrieved from Cloudinary as '{dest}' on attempt {attempt}")
                return True
            else:
                raise Exception("File URL not found")
        except Exception as e:
            print(f"Error retrieving file on attempt {attempt}: {str(e)}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    print(f"Max retry attempts reached. File download failed.")
    return False