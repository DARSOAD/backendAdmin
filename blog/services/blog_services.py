# blog/services/blog_services.py

from datetime import datetime
import uuid
import logging

from fastapi.encoders import jsonable_encoder

from blog.db.models.blog_models import BlogPost
from blog.db.schemas.blog_schemas import BlogPostCreate
from blog.utils.s3_utils import upload_base64_image
from core.client import dynamodb  # wrapper para DynamoDB

logger = logging.getLogger(__name__)

blogposts_table = dynamodb.Table("blog_posts")

def safe_upload(image_base64, author_id, folder):
    try:
        if image_base64:
            return upload_base64_image(image_base64, author_id, folder)
    except Exception as e:
        raise ValueError("Error al subir la imagen. Asegúrate de que esté en base64 válido.") from e
    return None

def create_post(data: BlogPostCreate, author_id: str, author_name: str) -> BlogPost:
    post_id = str(uuid.uuid4())
    created_at = datetime.utcnow()

    cover_url = None
    thumbnail_url = None
    if data.cover and not data.cover.startswith("http"):
        cover_url = safe_upload(data.cover, author_id, "cover")
    if data.thumbnail and not data.thumbnail.startswith("http"):
        thumbnail_url = safe_upload(data.thumbnail, author_id, "thumbnail")
    

    post = BlogPost(
        post_id=post_id,
        title=data.title,
        content=data.content,
        cover_url=cover_url,
        thumbnail_url=thumbnail_url,
        author_id=author_id,
        author_name=author_name,
        created_at=created_at,
    )
    print(f"Creando post: {post}")
    try:
        blogposts_table.put_item(Item=jsonable_encoder(post))
        logger.info(f"Nuevo post creado por {author_name} (ID: {author_id}) con ID {post_id}")
    except Exception as e:
        logger.error(f"Error al crear el post: {e}")
        raise ValueError("Error al crear el post en la base de datos.") from e
    
    return post


