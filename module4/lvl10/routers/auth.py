from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from security import create_access_token
from services.users import UserServiceDep

router = APIRouter(tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/token")
async def login_for_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()], service: UserServiceDep):
    user = await service.authenticate(form.username, form.password)
    return Token(access_token=create_access_token({"sub": user.email, "role": user.role}))
