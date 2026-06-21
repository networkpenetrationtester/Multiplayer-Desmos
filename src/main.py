import asyncio
import json
import secrets
from datetime import datetime
from hashlib import sha256
from random import randint

import psycopg2
import redis
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from psycopg2.sql import SQL, Identifier, Placeholder
from pydantic import ValidationError
from ulid import ULID

from src.modules.objects import *
from src.modules.requests import *
from src.modules.responses import *

# TODO: ENV VARIABLES
# every ID will be a ULID
# tokens will be bearerauth, what kinda token tho ? static ???
# refreshtoken ?
# redis keys: room:<roomid> -> { content: { expression: <expr>, owner: <userid> }[] }
# redis keys:


rd = redis.Redis(
    host="localhost",
    username="default",
    password="desmos",
    port=6379,
    db=0,
    decode_responses=True,
)
pg_conn = psycopg2.connect(dbname="desmos", user="desmos", password="desmos", port=5432)
pg_cur = pg_conn.cursor()
app = FastAPI()
ph = PasswordHasher()

pg_cur.execute(
    """CREATE TABLE IF NOT EXISTS users (
        id TEXT NOT NULL PRIMARY KEY,
        display_name TEXT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )"""
)

pg_cur.execute(
    """CREATE TABLE IF NOT EXISTS graphs (
        id TEXT NOT NULL PRIMARY KEY,
        owner_id TEXT NOT NULL,
        name TEXT NOT NULL UNIQUE,
        content TEXT NOT NULL
    )"""
)

pg_conn.commit()


def APIResponse(
    success: bool,
    failure_code: FAILURE_CODES | None = None,
    message: str | None = None,
    data: dict[str, Any] | None = None,
):

    d = dict()
    d["success"] = success
    if failure_code:
        d["failure_code"] = failure_code
    if message:
        d["message"] = message
    if data:
        d["data"] = data

    return d


def AddUser(user: User):
    existing_user = GetUserByUsername(user.username)

    if not existing_user:
        pg_cur.execute(
            SQL("INSERT INTO users VALUES (%s, %s, %s, %s)"),
            (
                user.id,
                user.display_name,
                user.username,
                user.password_hash,
            ),
        )
        pg_conn.commit()

        return user


def RemoveUser(user: User):
    pass


def GetUserByUsername(username: str):
    pg_cur.execute(
        SQL("SELECT * FROM users WHERE username = %s"),
        (username,),
    )

    user = pg_cur.fetchone()

    if user:
        (id, display_name, username, password_hash) = user

        return User(
            id=id,
            display_name=display_name,
            username=username,
            password_hash=password_hash,
        )


def GetUserByID(id: str):
    pg_cur.execute(
        SQL("SELECT * FROM users WHERE id = %s"),
        (id,),
    )

    user = pg_cur.fetchone()

    if user:
        (id, display_name, username, password_hash) = user

        return User(
            id=id,
            display_name=display_name,
            username=username,
            password_hash=password_hash,
        )


def GenerateToken():
    return sha256(
        string=str(secrets.SystemRandom().getrandbits(256)).encode()
    ).hexdigest()


def GetToken(userid: str):
    token = rd.get(f"user:{userid}:token")
    if not token:
        token = SetToken(userid)

    return token


def SetToken(userid: str):
    token = GenerateToken()
    rd_key = f"user:{userid}:token"
    rd.set(rd_key, token)
    rd.expire(rd_key, 60 * 60 * 24 * 30)

    return token


def CheckPassword(password_hash: str, password: str):
    try:
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except VerificationError:
        return False
    except InvalidHashError:
        return False


@app.get("/", response_class=HTMLResponse)
def _root():
    return open("www/index.html").read()


@app.get("/2d", response_class=HTMLResponse)
def _2d():
    return open("www/2d/index.html").read()


@app.get("/3d", response_class=HTMLResponse)
def _3d():
    return open("www/3d/index.html").read()


@app.post("/api/register", response_class=JSONResponse)
async def _register(request: RegisterRequest):  # TODO: APIResponse maker thing
    user = AddUser(
        User(
            id=str(ULID()),
            username=request.username,
            password_hash=ph.hash(request.password),
        )
    )

    if user:
        token = SetToken(user.id)

        return APIResponse(success=True, data={"token": token})
    else:
        return APIResponse(
            success=False,
            failure_code=FAILURE_CODES.USER_EXISTS,
            message="That user already exists.",
        )


@app.post("/api/login", response_class=JSONResponse)
async def _login(request: LoginRequest):
    user = GetUserByUsername(request.username)

    if user:
        if CheckPassword(user.password_hash, request.password):
            token = GetToken(user.id)

            return APIResponse(success=True, data={"token": token})
        else:
            return APIResponse(
                success=False,
                failure_code=FAILURE_CODES.PASSWORD_INVALID,
                message="That password is incorrect.",
            )
    else:
        return APIResponse(
            success=False,
            failure_code=FAILURE_CODES.USER_VOID,
            message="That user does not exist.",
        )


# BEARER
@app.post("/api/logout", response_class=JSONResponse)
async def _logout(request: Request):
    try:
        bearer = request.headers.get("authorization")
        if not bearer:
            return APIResponse(success=False, failure_code=FAILURE_CODES.TOKEN_INVALID)
        dict = await request.json()
        logout_request = LogoutRequest(**dict)
        if bearer is GetToken(logout_request.user_id):
            return APIResponse(success=True, message="Successfully logged out.")
    except ValidationError:
        pass

    return APIResponse(success=False, failure_code=FAILURE_CODES.GENERAL)


@app.get("/api/counts", response_class=JSONResponse)
def _counts():
    if randint(0, 100) > 50:
        return {"2d": randint(0, 1000), "3d": randint(0, 1000)}
    else:
        return {"2d": "?", "3d": "?"}


app.mount("/", StaticFiles(directory="www"))
