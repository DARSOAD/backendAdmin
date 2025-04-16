# blog/routes/blog_routes.py

from fastapi import APIRouter, Depends, HTTPException, logger, status, Query
from blog.db.schemas.blog_schemas import BlogPostCreate, BlogPostOut, BlogPostUpdate
from blog.services.blog_services import create_post, delete_post, get_paginated_posts, get_post_by_slug_or_id, update_post
from core.security import get_current_user
from typing import Dict, Optional

router = APIRouter(tags=["Blog"],
                responses={status.HTTP_404_NOT_FOUND:{"message":"Not found"}})


# Crear un post
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
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error (routers/blog_routes.py /create)")
    

# Modificar un post
@router.patch("/edit/{post_id}", response_model=BlogPostOut)
def edit_blog_post(
    post_id: str,
    payload: BlogPostUpdate,
    user=Depends(get_current_user)
):
    return update_post(post_id, payload, user["id"])


# Obtener un post por ID o slug
@router.get("/post/{slug_or_id}", response_model=BlogPostOut)
def get_blog_post(slug_or_id: str):
    return get_post_by_slug_or_id(slug_or_id)


# Obtener posts paginados
@router.get("/posts", response_model=dict)
def list_paginated_posts(
    page_token: Optional[str] = Query(None, alias="page"),
    limit: int = Query(10, ge=1, le=100)
):
    return get_paginated_posts(limit=limit, last_evaluated_key=page_token)


# Eliminar un post
@router.delete("/delete/{post_id}", status_code=200)
def delete_blog_post(post_id: str, user=Depends(get_current_user)):
    return delete_post(post_id, user["id"])