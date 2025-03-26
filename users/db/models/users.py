from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    name: str
    hashed_password: str
    role: str = "user"
    created_at: Optional[datetime] = None
