from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

from database import SessionDep
from redis_client import get_redis_client
from models import Role, User
from repositories.users import UserRepository
from security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token expired") from None
    except jwt.InvalidTokenError:
        raise _unauthorized("Could not validate credentials") from None

    email = payload.get("sub")
    if email is None:
        raise _unauthorized("Could not validate credentials")

    user = await UserRepository(session).get_by_email(email)
    if user is None:  # токен справжній, але користувача вже немає
        raise _unauthorized("User not found")
    if not user.is_active:  # токен чинний, але акаунт вимкнено
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: Role):
    async def checker(user: CurrentUser) -> User:
        if user.role not in roles:  # роль беремо з бази, а не з токена
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user

    return checker


ManagerUser = Annotated[User, Depends(require_role(Role.MANAGER, Role.ADMIN))]
AdminUser = Annotated[User, Depends(require_role(Role.ADMIN))]


RedisDep = Annotated[Redis, Depends(get_redis_client)]