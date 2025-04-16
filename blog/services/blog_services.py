# blog/services/blog_services.py

from datetime import datetime
from fastapi import HTTPException
import uuid
import logging
from fastapi.encoders import jsonable_encoder
from blog.db.models.blog_models import BlogPost
from blog.db.schemas.blog_schemas import BlogPostCreate, BlogPostUpdate
from blog.utils.s3_utils import upload_base64_image
from core.client import dynamodb  # wrapper para DynamoDB
import re
import unicodedata
from typing import Optional, Any

logger = logging.getLogger(__name__)

blogposts_table = dynamodb.Table("blog_posts")

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text

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

    # Validación y creación del slug
    slug = slugify(data.slug) or slugify(data.title)

    # Validar que no esté repetido
    existing = blogposts_table.scan(
        FilterExpression="slug = :slug_val",
        ExpressionAttributeValues={":slug_val": slug}
    )
    if existing.get("Count", 0) > 0:
        raise HTTPException(status_code=400, detail="Slug ya está en uso. Usa otro o cambia el título.")
    
    cover_url = None
    thumbnail_url = None
    if data.cover and not data.cover.startswith("http"):
        cover_url = safe_upload(data.cover, author_id, "cover")
    if data.thumbnail and not data.thumbnail.startswith("http"):
        thumbnail_url = safe_upload(data.thumbnail, author_id, "thumbnail")
    

    post = BlogPost(
        post_id=post_id,
        slug=slug,
        title=data.title,
        content=data.content,
        cover_url=cover_url,
        thumbnail_url=thumbnail_url,
        author_id=author_id,
        author_name=author_name,
        created_at=created_at,
    )
    try:
        blogposts_table.put_item(Item=jsonable_encoder(post))
        logger.info(f"Nuevo post creado por {author_name} (ID: {author_id}) con ID {post_id}")
    except Exception as e:
        logger.error(f"Error al crear el post: {e}")
        raise ValueError("Error al crear el post en la base de datos.") from e
    
    return post


def update_post(post_id: str, data: BlogPostUpdate, user_id: str) -> dict:
    existing = blogposts_table.get_item(Key={"post_id": post_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    update_data = {}

    # 🔤 Si se actualiza el título, también se puede regenerar slug (opcional, solo si no viene explícito)
    if data.title:
        update_data["title"] = data.title

    if data.content:
        update_data["content"] = data.content

    if data.cover:
        update_data["cover_url"] = (
            safe_upload(data.cover, user_id, "cover")
            if not data.cover.startswith("http")
            else data.cover
        )

    if data.thumbnail:
        update_data["thumbnail_url"] = (
            safe_upload(data.thumbnail, user_id, "thumbnail")
            if not data.thumbnail.startswith("http")
            else data.thumbnail
        )

    # ✅ Validación del slug si lo envía
    if data.slug:
        # Normalizar y validar
        new_slug = slugify(data.slug)

        # Si el nuevo slug ya existe en otro post, rechazar
        response = blogposts_table.scan(
            FilterExpression="slug = :slug_val AND post_id <> :post_id_val",
            ExpressionAttributeValues={
                ":slug_val": new_slug,
                ":post_id_val": post_id
            }
        )

        if response.get("Count", 0) > 0:
            raise HTTPException(status_code=400, detail="Este slug ya está en uso por otro post.")

        update_data["slug"] = new_slug

    update_data["updated_at"] = datetime.utcnow().isoformat()

    update_expr = "SET " + ", ".join(f"{k}=:{k}" for k in update_data)
    expr_values = {f":{k}": v for k, v in update_data.items()}

    blogposts_table.update_item(
        Key={"post_id": post_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )

    return {**existing, **update_data}



def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False

def get_post_by_slug_or_id(slug_or_id: str) -> BlogPost:
    try:
        if is_uuid(slug_or_id):
            # Buscar por post_id
            response = blogposts_table.get_item(Key={"post_id": slug_or_id})
            item = response.get("Item")
            if not item:
                raise HTTPException(status_code=404, detail="Post no encontrado")
            return BlogPost(**item)
        else:
            # Buscar por slug
            response = blogposts_table.scan(
                FilterExpression="slug = :slug_val",
                ExpressionAttributeValues={":slug_val": slug_or_id}
            )
            items = response.get("Items", [])
            if not items:
                raise HTTPException(status_code=404, detail="Post no encontrado")
            return BlogPost(**items[0])  # slugs son únicos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el post: {e}")
    

    
def get_paginated_posts(limit: int = 10, last_evaluated_key: Optional[str] = None) -> dict:
    scan_kwargs: dict[str, Any] = {"Limit": limit}

    if last_evaluated_key:
        scan_kwargs["ExclusiveStartKey"] = {"post_id": last_evaluated_key}

    try:
        response = blogposts_table.scan(**scan_kwargs)
        items = response.get("Items", [])
        posts = [BlogPost(**item) for item in items]

        return {
            "items": posts,
            "next_token": response.get("LastEvaluatedKey", {}).get("post_id"),  # Para usar como cursor
            "has_more": "LastEvaluatedKey" in response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener posts paginados: {e}")
    


def get_paginated_posts(limit: int = 10, last_evaluated_key: Optional[str] = None) -> dict:
    scan_kwargs: dict[str, Any] = {"Limit": limit}

    if last_evaluated_key:
        scan_kwargs["ExclusiveStartKey"] = {"post_id": last_evaluated_key}

    try:
        response = blogposts_table.scan(**scan_kwargs)
        items = response.get("Items", [])
        posts = [BlogPost(**item) for item in items]

        return {
            "items": posts,
            "next_token": response.get("LastEvaluatedKey", {}).get("post_id"),  # Para usar como cursor
            "has_more": "LastEvaluatedKey" in response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener posts paginados: {e}")


def delete_post(post_id: str, user_id: str):
    # Verifica si el post existe y pertenece al usuario
    response = blogposts_table.get_item(Key={"post_id": post_id})
    item = response.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    # if item["author_id"] != user_id:
    #     raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este post.")

    # Eliminar de DynamoDB
    blogposts_table.delete_item(Key={"post_id": post_id})

    return {"message": f"Post {post_id} eliminado correctamente"}