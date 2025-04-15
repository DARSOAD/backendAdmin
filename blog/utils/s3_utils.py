# blog/utils/s3_utils.py

import boto3
import base64
import uuid
from io import BytesIO
from fastapi import HTTPException
from core import config  
import re
import base64
from typing import Tuple

def decode_base64_image(data_url: str) -> Tuple[bytes, str]:
    """
    Separa y decodifica un data URL con encabezado MIME. 
    Retorna: (imagen en binario, tipo MIME)
    """
    match = re.match(r"data:(image/\w+);base64,(.+)", data_url)
    if not match:
        raise ValueError("Formato de imagen inválido. Se esperaba un data URL con encabezado MIME.")

    mime_type = match.group(1)  # image/jpeg, image/webp, etc.
    image_base64 = match.group(2)
    image_data = base64.b64decode(image_base64)
    return image_data, mime_type

def upload_base64_image(image_base64: str, author_id: str, folder: str = "posts") -> str:
    try:
        image_data, mime_type = decode_base64_image(image_base64)

        extension = mime_type.split("/")[-1]  # jpg, png, webp
        key = f"{folder}/{author_id}/{uuid.uuid4().hex}.{extension}"

        s3 = boto3.client(
            "s3",
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION
        )

        s3.upload_fileobj(
            Fileobj=BytesIO(image_data),
            Bucket=config.AWS_S3_BUCKET_NAME,
            Key=key,
            ExtraArgs={"ContentType": mime_type}
        )

        if config.AWS_S3_PUBLIC:
            return f"https://{config.AWS_S3_BUCKET_NAME}.s3.{config.AWS_REGION}.amazonaws.com/{key}"
        else:
            return s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": config.AWS_S3_BUCKET_NAME, "Key": key},
                ExpiresIn=3600
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen a S3: {e}")

