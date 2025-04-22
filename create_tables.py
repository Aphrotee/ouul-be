#!/usr/bin/env python3

import os
import enum
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Enum, ARRAY, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base


# Load the environment variables from the .env file
load_dotenv()

Base = declarative_base()

class AdminRole(str, enum.Enum):
    """Enum class defining the two types of admin roles"""
    superuser = "superuser"
    manager = "manager"
    admin = "admin"
    supervisor = "supervisor"
    user = "user"

class BlogStatus(str, enum.Enum):
    """Enum class defining the possible values for a blog status."""
    draft = "draft"
    published = "published"
    deleted = "deleted"

class BaseModel(Base):
    """Basemodel for other database tables to inherit"""
    __abstract__ = True

    id = Column(String(60), index=True, primary_key=True, default=str(uuid4)) # object's unique id
    created_at = Column(DateTime, default=datetime.now) # object's creation date
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now) # object's update date

class Blog(BaseModel):
    """Blog data model"""
    __tablename__ = "blogs"

    author_id = Column(String(60), ForeignKey('admins.id'), nullable=False)
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=False)
    status = Column(Enum(BlogStatus), nullable=False)
    admins = relationship("Admin", back_populates="blogs")

class Admin(BaseModel):
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


environment = os.getenv("ENVIRONMENT")

if environment == 'test':
    database_url = os.getenv("POSTGRES_TEST_URI")
    print(database_url)
elif environment == 'production':
    database_url = os.getenv("POSTGRES_PROD_URI")

engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)