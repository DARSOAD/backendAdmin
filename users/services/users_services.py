from users.db.schemas.users_schemas import AuthResponse, UserCreate, UserLogin, UserLoginOut, UserOut
from core.security import create_access_token, create_refresh_token
from fastapi import HTTPException
from datetime import datetime
import bcrypt
from core.client import dynamodb
import logging
from uuid import uuid4


# Configura el registro
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

users_table = dynamodb.Table("cleaning_users_users")

def create_user(user: UserCreate) -> AuthResponse:
    try:
        if not user.email or not user.name or not user.password:
            raise HTTPException(status_code=400, detail="All fields are required")

        response = users_table.scan(
            FilterExpression="email = :email_val",
            ExpressionAttributeValues={":email_val": user.email}
        )
        if response["Count"] > 0:
            raise HTTPException(status_code=400, detail="Could not process the request")

        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')    # Hash de la contraseña
        
        user_id = str(uuid4())  # Generar un UUID único para el usuario

        # Verificar si la imagen es None y asignar un valor por defecto
        if user.image is None:
            user.image = "/images/default-avatar.png"

        item = {
            "id": user_id,
            "email": user.email,
            "name": user.name,
            "hashed_password": hashed_password,
            "role": user.role,
            "created_at": datetime.utcnow().isoformat(),
            "picture": user.image
        }

        users_table.put_item(Item=item)

        # Generar tokens
        try:
            access_token = create_access_token(data={"sub": user_id, "name":user.name, "role": user.role})
            refresh_token = create_refresh_token(data={"sub": user_id})
        except Exception as token_error:
            logger.error(f"Error generating tokens: {token_error}")
            raise HTTPException(status_code=500, detail="Error generating tokens")

        # Construir la respuesta
        try:
            return AuthResponse(
                user=UserOut(
                    id=user_id,
                    email=user.email,
                    name=user.name,
                    role=user.role,
                    picture=user.image,
                    created_at=item["created_at"]  # Include created_at here
                ),
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
        except Exception as response_error:
            logger.error(f"Error building AuthResponse: {response_error}")
            raise HTTPException(status_code=500, detail="Error building response")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error (users_services.py /create_user)")

def login_user(user: UserLogin) -> AuthResponse:
    if not user.email or not user.password:
            raise HTTPException(status_code=400, detail="All fields are required")
    db_user = users_table.scan(
            FilterExpression="email = :email_val",
            ExpressionAttributeValues={":email_val": user.email}
        )
    
    if db_user["Count"] == 0:        
         raise HTTPException(status_code=400, detail="Invalid credentials")
    
    db_user = db_user["Items"][0]

     # Verificar que la contraseña proporcionada coincide con el hash almacenado
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user["hashed_password"].encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Si la contraseña es correcta, generar los tokens
    access_token = create_access_token(data={"sub": db_user["id"], "name": db_user["name"], "role": db_user["role"]})
    refresh_token = create_refresh_token(data={"sub": db_user["id"]})
    
    # Construir la respuesta con los tokens y la información del usuario
    return AuthResponse(
        user=UserOut(
            id=db_user["id"],
            email=user.email,
            name=db_user["name"],
            role=db_user["role"],
            picture=db_user.get("picture"),
            created_at=db_user["created_at"]  # Include created_at here
        ),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )