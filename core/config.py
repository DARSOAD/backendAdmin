# core/config.py

import os
import json
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Cargar variables de entorno desde .env (para desarrollo local)
load_dotenv()

# ================================
# 🔐 SECRET KEY
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
# 🗄️ DynamoDB Config (Local o AWS)
# ================================
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")  # Ej: http://localhost:9000

# ================================
# ☁️ S3 Config
# ================================
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_S3_PUBLIC = os.getenv("AWS_S3_PUBLIC", "True").lower() in ("true", "1", "yes")

# ================================
# 🛢️ PostgreSQL o RDS (opcional)
# ================================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cleaning:admin@localhost/cleaning")
