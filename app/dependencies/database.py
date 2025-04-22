#!/usr/bin/env python3

""" Creates and generates a Database session """

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Load the environment variables from the .env file
load_dotenv()

environment = os.getenv("ENVIRONMENT")

if environment == 'test':
    database_url = os.getenv("POSTGRES_TEST_URI")
elif environment == 'production':
    database_url = os.getenv("POSTGRES_PROD_URI")

engine = create_engine(database_url, echo=True, pool_size=50, max_overflow=10)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Generates a new database session with dependency injection"""
    db = Session()
    try:
        yield db
    finally:
        db.close()