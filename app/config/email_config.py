#!/usr/bin/env python3

""" Module for configuring email delivery handler """

import os

from pathlib import Path
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig
from app.dependencies.error import httpError


# Load the environment variables from the .env file
load_dotenv()

username = os.getenv('MAIL_USERNAME')
password = os.getenv('MAIL_PASSWORD')
from_email = os.getenv('MAIL_FROM')
mail_server = os.getenv('MAIL_SERVER')
mail_port = os.getenv('MAIL_PORT')
from_name = os.getenv('MAIL_FROM_NAME')

if not username or not password:
    raise httpError(status_code=500, detail="Missing email configuration environment variables")

emailConfig = conf = ConnectionConfig(
    MAIL_USERNAME = username,
    MAIL_PASSWORD = password,
    MAIL_FROM = from_email,
    MAIL_PORT = int(mail_port),
    MAIL_SERVER = mail_server,
    MAIL_FROM_NAME = from_name,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER = "/home/aphrotee/ouul-be/app/templates/email"
)