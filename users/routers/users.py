from fastapi import APIRouter, HTTPException, status
from users.db.models.users import User
from users.db.schemas.users_schemas import UserCreate, UserOut
from users.services.users_services import create_user

router = APIRouter(tags=["users"],
                responses={status.HTTP_404_NOT_FOUND:{"message":"Not found"}})




@router.post("/register")
def register(user: UserCreate):
    try:
        return create_user(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    