from fastapi import APIRouter, HTTPException, status
from users.db.models.users import User
from users.db.schemas.users_schemas import AuthResponse, UserCreate, UserLogin, UserLoginOut
from users.services.users_services import create_user, login_user

router = APIRouter(tags=["users"],
                responses={status.HTTP_404_NOT_FOUND:{"message":"Not found"}})

@router.post("/register", response_model=AuthResponse, tags=["users"])
def register(user: UserCreate):
    try:
        return create_user(user)  
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post("/login", response_model=UserLoginOut, tags=["users"])
async def login(user: UserLogin):
    try:
        return login_user(user)  
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
