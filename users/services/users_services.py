import boto3
import bcrypt
from datetime import datetime
from users.db.schemas.users_schemas import UserCreate, UserOut
from fastapi import HTTPException
from users.db.schemas.client import dynamodb


users_table = dynamodb.Table("Users")

def create_user(user: UserCreate) -> UserOut:
    # 1️⃣ Validación de datos obligatorios
    if not user.email or not user.name or not user.password:
        raise HTTPException(status_code=400, detail="All fields are required")

    # 2️⃣ Verifica si ya existe ese usuario
    response = users_table.get_item(Key={"email": user.email})
    if "Item" in response:
        raise HTTPException(status_code=409, detail="The user is already registered")
    
    # Hashear contraseña
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Datos a guardar
    item = {
        "email": user.email,
        "name": user.name,
        "hashed_password": hashed_password,
        "role": "user",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Guardar en DynamoDB
    users_table.put_item(Item=item)

    return UserOut(
        email=user.email,
        name=user.name,
        role="admin"
    )
