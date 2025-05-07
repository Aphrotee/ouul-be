#!/usr/bin/env python3

"""module for deefining admin data model"""

import enum
from typing import List
from datetime import datetime
from app.models.models import Base, Basemodel, Response
from pydantic import BaseModel, EmailStr, UUID4
from sqlalchemy import Column, DateTime, String, Boolean, Enum, JSON
from sqlalchemy.orm import relationship

class UserType(str, enum.Enum):
    """Enum class defining the two types of user account types"""
    startup= "startup"
    investor = "investor"
    corporate = "corporate"
    accelerator = "accelerator"


class User(Basemodel, Base):
    """User data model"""
    __tablename__ = "users"

    firstname = Column(String, nullable=False, default="") # User's firstname
    lastname = Column(String, nullable=False, default="") # User's lastname
    email = Column(String, nullable=False) # User's email address
    password = Column(String, nullable=False, default="") # User's hashed password
    pin = Column(String, nullable=False, default="") # User's hashed PIN
    type = Column(Enum(UserType), nullable=False) # User account type
    isVerified = Column(Boolean, nullable=False, default=False)
    


    def __init__(self, **kwargs):
        """Initialize user data model"""
        super().__init__(**kwargs)
    
    def verify_password(self, password):
        """Verify admin's password"""
        return self.password == password


class UserSignupSchema(BaseModel):
    email: EmailStr # User's email address
    type: UserType # User aacount type

class UserOtpSchema(BaseModel):
    email: EmailStr # User's email address
    otp: str # User's otp for verification

class UserPasswordSchema(BaseModel):
    email: EmailStr # User's email address
    password: str # User's password

class UserPasswordResetSchema(BaseModel):
    email: EmailStr # User's email address
    password: str # User's password
    otp: str # User's otp for verification

class UserPINSchema(BaseModel):
    email: EmailStr # User's email address
    password: str # User's password
    pin: str # User's pin

class UserPINResetSchema(BaseModel):
    pin: str # User's pin
    otp: str # User's otp for verification

class UserResponseSchema(BaseModel):
    id: UUID4 # Admin's unique identifier
    created_at: datetime # Admin's creation date
    updated_at: datetime # Admin's update date
    firstname: str # Admin's username
    lastname: str # Admin's username
    email: EmailStr # Admin's email address
    type: UserType # User account type
    isVerified: bool # User verification check

class UserResponse(Response):
    data: UserResponseSchema # admin data

class loginResponseSchema(UserResponse):
    access_token: str # jwt session token
    token_type: str # the type of access token returned

class Data(BaseModel):
    count: int = 1
    admins: List[UserResponseSchema] 

class MultipleUserResponse(Response):
    data: Data