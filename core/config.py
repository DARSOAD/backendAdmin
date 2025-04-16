# core/config.py

import logging
import os
import json
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# ================================
# 🌍 Cargar variables desde .env (solo en desarrollo)
# ================================
load_dotenv()

# ================================
# 🔐 SECRET KEY desde Secrets Manager o .env
# ================================
def get_secret_key() -> str:
    try:
        secret_name = os.getenv("SECRET_NAME", "CleaningApp")
        region_name = os.getenv("AWS_REGION", "ap-southeast-2")

        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])
        return secret["SECRET_KEY"]
    except ClientError as e:
        print(f"[INFO] No se pudo obtener el secreto desde Secrets Manager. Usando .env. ({e})")
    except Exception as e:
        print(f"[ERROR] Falla inesperada con Secrets Manager: {e}")

    # Modo local o fallback
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY no está definida ni en Secrets Manager ni en .env")
    return secret_key

# ================================
# 🔐 JWT Config
# ================================
SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ================================
# 🗄️ DynamoDB Config
# ================================
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")  # Solo se usa en local

# ================================
# ☁️ S3 Config (bucket y cliente)
# ================================
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_S3_PUBLIC = os.getenv("AWS_S3_PUBLIC", "True").lower() in ("true", "1", "yes")

# Crear cliente S3
if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
    # 🧪 Modo local con .env
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
else:
    try:
        # ☁️ Modo producción: usa IAM Role del contenedor (App Runner)
        s3_client = boto3.client("s3", region_name=AWS_REGION)
        print("[INFO] Cliente S3 configurado en modo PRODUCCIÓN con IAM Role. {s3_client}")
    except Exception as e:
        logging.error(f"[ERROR] Fallo al configurar cliente S3 en App Runner: {e} ")
        raise RuntimeError("No se pudo configurar el cliente S3 en producción")

# ================================
# 🛢️ PostgreSQL o RDS (opcional)
# ================================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cleaning:admin@localhost/cleaning")
