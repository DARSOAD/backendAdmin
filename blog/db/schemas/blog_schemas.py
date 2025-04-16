# blog/db/schemas/blog_schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=10)
    cover: Optional[str]  # Imagen opcional en base64
    thumbnail: Optional[str]  # Imagen opcional en base64
    slug: Optional[str] = None  # Slug opcional para SEO, se generará automáticamente si no se proporciona

class BlogPostOut(BaseModel):
    post_id: str
    title: str
    slug: Optional[str]
    content: str
    cover_url: Optional[str]
    thumbnail_url: Optional[str]
    author_id: str
    author_name: str
    created_at: datetime
    
class BlogPostUpdate(BaseModel):
    title: Optional[str] = None 
    content: Optional[str] = None 
    cover: Optional[str] = None  # base64 o URL existente
    thumbnail: Optional[str] = None  # base64 o URL existente
    slug: Optional[str] = None  # Slug opcional para SEO, se generará automáticamente si no se proporciona