from typing import Dict
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
import jwt
import datetime
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, Header
import jwt
import time
from .models import User
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Wefi API",
    description="API for Wefi",
    version="0.1.0",
    docs_url="/",
    redoc_url=None,
    openapi_url="/openapi.json",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_scheme = HTTPBearer()


class UserIn(BaseModel):
    balance: int


class UserOut(BaseModel):
    username: str
    balance: int


def generate_token(username: str) -> str:
    dt = datetime.now() + timedelta(days=60)
    token = jwt.encode({
        'username': username,
        'exp': dt.utcfromtimestamp(dt.timestamp())},
        'secret', algorithm='HS256')
    return token


@app.post("/users/{username}", tags=["Users"], description="Create a new user")
async def create_user(username: str, user: UserIn):
    user = User.get(username)
    return {"user": user, "token": generate_token(username)}


@app.post("/deposit", tags=["Transactions"])
async def deposit(username: str, amount: int, authorization: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        token = authorization.credentials
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        raise HTTPException(status_code=400, detail="Not authorized")
    balance = User.deposit(username, amount)
    return {"username": username, "balance": balance}


@app.post("/send", tags=["Transactions"])
async def send(from_username: str, to_username: str, amount: int, authorization: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        token = authorization.credentials
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        raise HTTPException(status_code=400, detail="Not authorized")
    resp = User.transfer(from_username, to_username, amount)
    return resp


@app.get("/balance", tags=["Transactions"])
async def balance(username: str, authorization: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        token = authorization.credentials
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        raise HTTPException(status_code=400, detail="Not authorized")

    balance = User.get_balance(username)

    return balance
