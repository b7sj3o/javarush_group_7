import random
from typing import Annotated, Literal

from fastapi import FastAPI, Header, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="Extra demos")


@app.get("/dice", tags=["fun"])
def roll(sides: Annotated[int, Query(ge=2, le=100)] = 6, count: Annotated[int, Query(ge=1, le=10)] = 1):
    """Кидає кубики. Цей docstring стане описом у Swagger."""
    rolls = [random.randint(1, sides) for _ in range(count)]
    return {"rolls": rolls, "total": sum(rolls)}

RATES = {"USD": 41.5, "EUR": 48.3, "PLN": 11.3}   # умовні курси для демо

@app.get("/convert", tags=["fun"])
def convert(amount: Annotated[float, Query(gt=0)], to: Literal["USD", "EUR", "PLN"] = "USD"):
    return {"uah": amount, to: round(amount / RATES[to], 2)}


@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}


@app.get("/whoami")
def whoami(request: Request, user_agent: Annotated[str | None, Header()] = None):
    return {"ip": request.client.host, "user_agent": user_agent, "url": str(request.url)}


@app.get("/get-ip")
async def get_ip(request: Request):
    # Check for X-Forwarded-For header first, then fall back to direct connection host
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # X-Forwarded-For can contain a comma-separated list of IPs; the first one is the client
        client_ip = x_forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "Unknown"
        
    return {"ip": client_ip}


@app.get("/hello", response_class=HTMLResponse)
def hello_html(name: str = "студент"):
    return f"<h1>Привіт, {name}!</h1>"


@app.get("/old-docs", include_in_schema=False)
def old_docs():
    return RedirectResponse("/docs")


@app.get("/legacy", deprecated=True, tags=["old"])
def legacy():
    return {"use": "/dice"}
