import base64
import json
from datetime import UTC, datetime, timedelta

import jwt


SECRET_KEY = "aaswonaswn9c9a@*@AFskUMAY*@hy9a7nh82mcS*A(HkbsjC AYU:as)"
ALGORITHM = "HS256"


token = jwt.encode(
    payload={
        "sub": "email@example.com",
        "username": "testuser",
        "exp": datetime.now() + timedelta(minutes=30)
    },
    key=SECRET_KEY,
    algorithm=ALGORITHM
)


h, p, s = token.split(".")

token = f"{h}d.{p}.{s}"

print(jwt.decode(token, SECRET_KEY, ALGORITHM, options={"verify_signature": False}))