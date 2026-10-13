"""
Код зі слайдів рівня 4 «Аутентифікація та авторизація» — усе в одному файлі, щоб його
можна було запустити й потикати у Swagger:

    uv run uvicorn lesson:app --reload

Це НЕ частина проєкту бібліотеки (main.py + routers/), а матеріал презентації як є.
Там, де довелося відійти від слайда, щоб код узагалі працював, стоїть коментар «СЛАЙД:».
"""

from datetime import datetime, timedelta, timezone

import jwt  # СЛАЙД: `pip install "python-jose[cryptography]"` і `from jose import JWTError, jwt`; у нас PyJWT
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()


# ---------------------------------------------------------------------------
# Слайд «Налаштування аутентифікації у FastAPI»
# ---------------------------------------------------------------------------

# Створюємо екземпляр схеми. 'token' — це URL, де клієнт може отримати токен.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Захищений ендпоінт
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # У змінній 'token' буде вміст токена, який витягнуто із заголовка.
    # Далі ми будемо його перевіряти.
    return {"token": token}


# ---------------------------------------------------------------------------
# Слайд «Генерація та перевірка JWT-токенів»
# ---------------------------------------------------------------------------

# --- Налаштування ---
SECRET_KEY = "a_very_secret_key_should_be_in_env_variables"  # Зберігати в .env!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --- Функції ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:  # СЛАЙД: except JWTError (python-jose)
        return None  # Або згенерувати виняток


# ---------------------------------------------------------------------------
# Слайд «Захист ендпоінтів через JWT»
# ---------------------------------------------------------------------------


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    # Тут можна додати запит до БД для отримання об'єкта User за username
    # user = get_user_from_db(username=username)
    # if user is None: raise credentials_exception
    return {"username": username}  # Повертаємо дані користувача з токена


# СЛАЙД: `from . import auth` і `auth.get_current_user` — у нас усе в одному файлі
@app.get("/users/profile/me")
async def read_my_profile(current_user: dict = Depends(get_current_user)):
    # Якщо код дійшов сюди, це означає, що токен валідний.
    # У current_user знаходяться дані з payload токена.
    return current_user


# ---------------------------------------------------------------------------
# Слайд «Приклад: ендпоінт для входу (отримання токена)»
# ---------------------------------------------------------------------------
# СЛАЙД: `status` тут не імпортовано — на невдалому логіні був би NameError


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Тут має бути перевірка користувача в БД
    # user = authenticate_user(form_data.username, form_data.password)
    # Для прикладу вважаємо, що пароль вірний, якщо він не порожній
    if not form_data.password:  # Імітація перевірки
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    # Створюємо токен для користувача
    access_token = create_access_token(
        data={"sub": form_data.username, "roles": ["user"]}  # "sub" — стандартне ім'я для суб'єкта
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# Слайд «Обмеження доступу за ролями»
# ---------------------------------------------------------------------------
# СЛАЙД (баг для демонстрації): get_current_user повертає лише {"username"}, ролі з
# токена туди не потрапляють -> roles завжди [] -> обидва ендпоінти нижче дають 403
# навіть з валідним токеном. Виправлення — у проєкті (dependencies.py, розділ 7 конспекту).


def require_role(required_role: str):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        roles = current_user.get("roles", [])
        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return Depends(role_checker)


# Цей ендпоінт доступний лише користувачам з роллю 'admin' у токені
@app.get("/admin/dashboard")
async def get_admin_dashboard(admin_user: dict = require_role("admin")):
    return {"message": f"Welcome to the admin dashboard, {admin_user['username']}!"}


# Цей ендпоінт доступний користувачам з роллю 'user'
@app.get("/user/data")
async def get_user_data(user: dict = require_role("user")):
    return {"data": "some user-specific data"}
