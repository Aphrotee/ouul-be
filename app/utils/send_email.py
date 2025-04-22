#!/usr/bin/env python3

""" Module for handling Email delivery """
import os
import time
import requests

from dotenv import load_dotenv
from pydantic import EmailStr


load_dotenv()

# Initialize Jinja2 environment for template rendering
# env = Environment(loader=FileSystemLoader("/home/aphrotee/bloomsite-be/app/templates/email"))
max_retries = int(os.getenv("FILE_UPLOAD_MAX_RETRIES"))
retry_delay = int(os.getenv("FILE_UPLOAD_RETRY_DELAY"))

def send_email_background(subject: str, email_to: EmailStr, firstname: str, htmlBody: str):
    """Send email in the background with retry mechanism"""
    fromAddress = os.getenv("MAIL_FROM")
    apiKey = os.getenv("ZEPTOMAIL_API_KEY")
    
    requestBody = {
        "from": {
            "address": fromAddress
        },
        "to": [
            {
                "email_address": {
                    "address": email_to,
                    "name": firstname
                }
            }
        ],
        "subject": subject,
        "htmlbody": htmlBody
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{apiKey}"
    }

    url = "https://api.zeptomail.com/v1.1/email"
    for attempt in range(1, max_retries + 1):
        # Send the email
        response = requests.post(url, headers=headers, json=requestBody)
        if 200 < response.status_code < 400:
            print("({}) Email sent successfully to {}".format(response.status_code, email_to))
            return
        else:
            print(f"Error sending email on attempt {attempt}: {response.json()}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    print(f"Max retry attempts reached. Error sending email.")
    
    # message = MessageSchema(
    #     subject=subject,
    #     recipients=[email_to],
    #     template_body=body,
    #     subtype=MessageType.html,
    # )

    # fm = FastMail(emailConfig)

    # background_tasks.add_task(
    #     fm.send_message, message, template_name=template_name)