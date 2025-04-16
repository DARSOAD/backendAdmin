# blog/routes/blog_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from blog.db.schemas.blog_schemas import BlogPostCreate, BlogPostOut
from blog.services.blog_services import create_post
from core.security import get_current_user
from typing import Dict

router = APIRouter(tags=["Blog"],
                responses={status.HTTP_404_NOT_FOUND:{"message":"Not found"}})

@router.post("/create", response_model=BlogPostOut, status_code=status.HTTP_201_CREATED)
def create_blog_post(
    payload: BlogPostCreate,
    user: Dict = Depends(get_current_user)
):
  
    
    try:
        return  create_post(
        data=payload,
        author_id=user["id"],
        author_name=user["name"]
    )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error (routers/blog_routes.py /create)")
