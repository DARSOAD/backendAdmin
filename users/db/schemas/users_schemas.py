from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional
import re

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)  # Define restricciones de longitud
    role: str = Field(..., pattern=r'^(user|moderator|editor|manager|admin)$')  # Verifica si es user, moderator o admin
    password: str = Field(..., min_length=8)  # Longitud mínima de la contraseña
    image: Optional[str] = "/images/default-avatar.png"  # Campo opcional para la imagen

    @model_validator(mode="after")  # Reemplaza root_validator con 
    def validate_password(cls, values):
        password = values.password
        if not re.search(r'[A-Z]', password):
            raise ValueError("The password must contain at least one uppercase letter.")
        if not re.search(r'\d', password):
            raise ValueError("The password must contain at least one number.")
        if not re.search(r'[@$!%*?&]', password):
            raise ValueError("The password must contain at least one special character.")
        return values

    class Config:
        from_attributes = True  # Actualiza 'orm_mode' a 'from_attributes'

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    picture: str
    created_at: Optional[str]  # Opcional si decides incluir la fecha de creación del usuario

    class Config:
        from_attributes = True  # Actualiza 'orm_mode' a 'from_attributes'

class AuthResponse(BaseModel):
    user: UserOut
    access_token: str
    refresh_token: str
    token_type: str  = "bearer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    class Config:
        from_attributes = True  # Actualiza 'orm_mode' a 'from_attributes'

class UserLoginOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str  = "bearer"