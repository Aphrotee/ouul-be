#!/usr/bin/env python3

""" Creates and generates a Database session """

import os
import redis
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Load the environment variables from the .env file
load_dotenv()

# environment = os.getenv("ENVIRONMENT")

# if environment == 'test':
#     database_url = os.getenv("POSTGRES_TEST_URI")
# elif environment == 'production':
#     database_url = os.getenv("POSTGRES_PROD_URI")

def get_cache():
    """Generates a new redis session with dependency injection"""
    r = redis.Redis()
    try:
        yield r
    finally:
        r.close()