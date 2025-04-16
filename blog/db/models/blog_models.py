# blog/db/models/blog_models.py
from pydantic import BaseModel  
from typing import Optional
from datetime import datetime

class BlogPost(BaseModel):
    post_id: str
    slug: Optional[str]
    title: str
    content: str
    cover_url: Optional[str]
    thumbnail_url: Optional[str]
    author_id: str
    author_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
