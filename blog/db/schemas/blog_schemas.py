# blog/db/schemas/blog_schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=10)
    cover: Optional[str]  # Imagen opcional en base64
    thumbnail: Optional[str]  # Imagen opcional en base64

class BlogPostOut(BaseModel):
    post_id: str
    title: str
    content: str
    cover_url: Optional[str]
    thumbnail_url: Optional[str]
    author_id: str
    author_name: str
    created_at: datetime
    