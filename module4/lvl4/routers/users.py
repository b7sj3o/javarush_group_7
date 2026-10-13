from fastapi import APIRouter, Depends, status, HTTPException

from dependencies import AdminUser, oauth2_scheme
from models import UserCreate, UserOut, get_user_by_email, add_user, users_db
from security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate):
    if get_user_by_email(data.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Такий email вже зайнятий"
        )
    
    user = add_user(data.name, data.email, data.password.get_secret_value())
    
    return user
    
    

@router.get("", response_model=list[UserOut])
async def list_users(admin: AdminUser):
    return list(users_db.values())