#!/usr/bin/env python3

"""module for deefining blog data model"""


import enum
from datetime import datetime
from app.models.models import Base, Basemodel, Response
from pydantic import BaseModel, UUID4
from sqlalchemy import Column, ForeignKey, String, ARRAY, Enum
from sqlalchemy.orm import relationship
from typing import List

class BlogStatus(str, enum.Enum):
    """Enum class defining the possible values for a blog status."""
    draft = "draft"
    published = "published"
    deleted = "deleted"


class Blog(Basemodel, Base):
    """Blog data model"""
    __tablename__ = "blogs"

    author_id = Column(String, ForeignKey('admins.id'), nullable=False) # id of the admin that created the blog (author)
    author = Column(String, nullable=False) # username of author
    title = Column(String, nullable=False) # blog title
    content = Column(String, nullable=False) # blog content
    tags = Column(ARRAY(String), nullable=False) # blog tags
    status = Column(Enum(BlogStatus), nullable=False) # blog status
    admins = relationship("Admin", back_populates="blogs") # blog author's data


class BlogUploadSchema(BaseModel):
    title: str # blog title
    content : str # blog content
    status: BlogStatus # blog status (draft/published)
    tags: List[str] # blog tags

class BlogUpdateSchema(BaseModel):
    title: str # blog title
    content : str # blog content
    status: BlogStatus # blog status (draft/published)
    tags: List[str] # blog tags

class BlogResponseSchema(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    author_id: str
    author: str
    title: str
    content: str
    status: BlogStatus
    tags: List[str]

class SingleBlogResponse(Response):
    data: BlogResponseSchema

class Data(BaseModel):
    count: int # number of returned blogs
    blogs: List[BlogResponseSchema]

class MultipleBlogsResponse(Response):
    data: Data