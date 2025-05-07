#!/usr/bin/env python


import bcrypt, os
from app.dependencies.error import httpError
from app.models.admins import Admin
from app.models.users import User
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

secret_key = os.getenv("JWT_SECRET_KEY")
algorithm = os.getenv("JWT_ALGORITHM")


def check_adminSignupSchema(admin: dict, db: Session):
    """
    Checks if all required fields are provided for admin registration
    and confirms if the admin exists
    """
    if admin.get("email") is None or len(admin.get("email")) == 0: # type: ignore
        # Checks if email address is provided
        raise httpError(status_code=400, detail="Email address is required")
    elif admin.get("username") is None or len(admin.get("username")) == 0: # type: ignore
        # Checks if first name is provided
        raise httpError(status_code=400, detail="Admin username is required")
    elif admin.get("password") is None or len(admin.get("password")) == 0: # type: ignore
        # Checks if password is provided
        raise httpError(status_code=400, detail="Password is required")
    elif db.query(Admin).filter(Admin.email == admin.get("email")).first() is not None: # type: ignore
        # Checks if user already exists with supplied email address
        raise httpError(status_code=400, detail="Admin already exists")
    elif db.query(Admin).filter(Admin.username == admin.get("username")).first() is not None:
        # Checks if user already exists with supplied username
        raise httpError(status_code=400, detail="Admin already exists")

def hash_password(password: str):
    """
    Hashes admin's password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta):
    """
    Creates a jwt token for admnin login session
    """
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm)
    return encoded_jwt

def validate_admin(token: str) -> str:
    """
    Validates a admin's jwt token to identify the admin
    """
    credentials_exception = httpError(status_code=401, detail="Request not authorized")
    try:
        payload: dict = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = str(payload.get("adminEmail"))
        id: str = str(payload.get("adminId"))
        if email is None:
            print("No email")
            raise credentials_exception
        if id is None:
            print("No admin id")
            raise credentials_exception
        return id
    except JWTError as e:
        print("jwt err: {}".format(str(e)))
        raise credentials_exception

def validate_user(token: str) -> str:
    """
    Validates a user's jwt token to identify the user
    """
    credentials_exception = httpError(status_code=401, detail="Request not authorized")
    try:
        payload: dict = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = str(payload.get("userEmail"))
        id: str = str(payload.get("userId"))
        if email is None:
            print("No email")
            raise credentials_exception
        if id is None:
            print("No user id")
            raise credentials_exception
        return id
    except JWTError as e:
        print("jwt err: {}".format(str(e)))
        raise credentials_exception

def get_admin(Id: str, db: Session) -> Admin:
    """
    Checks if there is an admin with the id passed as a parameter
    """
    try:
        admin: Admin = db.query(Admin).filter_by(id = Id).first()
        return admin
    except Exception as e:
        print("Error: {}".format(str(e)))
        raise httpError(status_code=400, detail="Bad request")

def get_user(Id: str, db: Session) -> User:
    """
    Checks if there is an admin with the id passed as a parameter
    """
    try:
        user: User = db.query(User).filter_by(id = Id).first()
        return user
    except Exception as e:
        print("Error: {}".format(str(e)))
        raise httpError(status_code=400, detail="Bad request")

def verify_password(password: str, hashed: str) -> bool:
    """
    Verifies admin's password
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
