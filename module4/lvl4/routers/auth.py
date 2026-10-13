from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from models import get_user_by_email
from security import create_access_token, verify_password

router = APIRouter(tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/token")
async def login_for_access_token(form: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return Token(access_token=create_access_token({"sub": user.email, "role": user.role}))
