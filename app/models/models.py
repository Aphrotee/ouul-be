#!/usr/bin/env python3

from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

Base = declarative_base()

def create_uuid4_string() -> str:
    "Create a uuid4 and return it as string "
    return str(uuid4())

class Basemodel:
    """Basemodel for other database tables to inherit"""
    __abstract__ = True

    id = Column(String(60), index=True, primary_key=True, default=create_uuid4_string) # object's unique id
    created_at = Column(DateTime, default=datetime.now) # object's creation date
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now) # object's update date

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key != '__class__':
                setattr(self, key, value)
    
    def save(self, session: Session):
        """Save object to database"""
        self.updated_at = datetime.now()
        session.add(self)
        session.commit()
    
    def to_dict(self):
        """returns a dictionary containing all keys/values of the instance"""
        new_dict = self.__dict__.copy()
        if "__class__" in new_dict:
            del new_dict["__class__"]
        if "password" in new_dict:
            del new_dict["password"]
        if "_sa_instance_state" in new_dict:
            del new_dict["_sa_instance_state"]
        return new_dict

    def update(self, session: Session, **kwargs):
        """Update object in database"""
        for key, value in kwargs.items():
            if key != '__class__' and key != 'id' and key != 'created_at'and key != 'author_id' and key != 'author':
                setattr(self, key, value)
        self.updated_at = datetime.now()
        session.commit()

class Response(BaseModel):
    success: bool # response status
    message: str # response message