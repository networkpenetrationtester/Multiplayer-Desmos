from enum import Enum
from random import randint

import psycopg2
import redis
from argon2 import PasswordHasher
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from psycopg2.sql import SQL, Identifier, Placeholder
from src.modules.objects import *
from src.modules.requests import *
from src.modules.responses import *
from ulid import ULID

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


def CheckBearer():
    pass


def CheckPassword(password_hash: str, password: str):
    return ph.verify(password_hash, password)


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
def _register(request: RegisterRequest):  # TODO: APIResponse maker thing
    user = AddUser(
        User(
            id=str(ULID()),
            username=request.username,
            password_hash=ph.hash(request.password),
        )
    )
    return user is not None


@app.post("/api/login", response_class=JSONResponse)
def _login(request: LoginRequest):
    user = GetUserByUsername(request.username)
    return user and CheckPassword(user.password_hash, request.password)


@app.get("/api/counts", response_class=JSONResponse)
def _counts():
    if randint(0, 100) > 50:
        return {"2d": randint(0, 1000), "3d": randint(0, 1000)}
    else:
        return {"2d": "?", "3d": "?"}


app.mount("/", StaticFiles(directory="www"))
