#!/usr/bin/env python3

"""module for deefining admin data model"""

import enum
from typing import List
from datetime import datetime
from app.models.models import Base, Basemodel, Response
from pydantic import BaseModel, EmailStr, UUID4
from sqlalchemy import Column, DateTime, String, Boolean, Enum, JSON
from sqlalchemy.orm import relationship

class AdminRole(str, enum.Enum):
    """Enum class defining the two types of admin roles"""
    user = "user"
    superuser = "superuser"
    manager = "manager"
    admin = "admin"
    supervisor = "supervisor"


class Admin(Basemodel, Base):
    """Admin data model"""
    __tablename__ = "admins"

    username = Column(String, nullable=False) # Admin's username
    email = Column(String, nullable=False) # Admin's email address
    password = Column(String, nullable=False) # Admin's hashed password.
    is_active = Column(Boolean, nullable=True, default=True) # Admin's account status (active/inactive)
    last_login = Column(DateTime, default=datetime.now) # Last time admin was active
    role = Column(Enum(AdminRole), nullable=False, default="user") # Admin's role (editor/admin)
    permissions = Column(JSON, nullable=False, default="{}")
    blogs = relationship("Blog", back_populates="admins")


    def __init__(self, **kwargs):
        """Initialize user data model"""
        super().__init__(**kwargs)
    
    def verify_password(self, password):
        """Verify admin's password"""
        return self.password == password


class AdminSignupSchema(BaseModel):
    username: str # Admin's username
    email: EmailStr # Admin's email address
    password: str # Admin's password
    role: AdminRole # Admin's role (manager/admin/supervisor/user)
    permissions: dict # Admin's permissions (create/read/update/delete)

class AdminResponseSchema(BaseModel):
    id: UUID4 # Admin's unique identifier
    created_at: datetime # Admin's creation date
    updated_at: datetime # Admin's update date
    username: str # Admin's username
    email: EmailStr # Admin's email address
    is_active: bool # Admin's account status (True->active/False->inactive)
    last_login: datetime # Last time admin was active
    role: AdminRole # Admin's role (superuser/manager/admin/supervisor/user)
    permissions: dict

class AdminResponse(Response):
    data: AdminResponseSchema # admin data

class loginResponseSchema(AdminResponse):
    access_token: str # jwt session token
    token_type: str # the type of access token returned

class Data(BaseModel):
    count: int = 1
    admins: List[AdminResponseSchema] 

class MultipleAdminResponse(Response):
    data: Data