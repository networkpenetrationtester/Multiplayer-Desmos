import psycopg2
import redis
from psycopg2.sql import SQL

from modules.env import (
    POSTGRES_DATABASE,
    POSTGRES_HOSTNAME,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USERNAME,
    REDIS_DATABASE,
    REDIS_HOSTNAME,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_USERNAME,
)
from modules.objects import User
from modules.stateless import GenerateToken

rd = redis.Redis(
    host=REDIS_HOSTNAME,
    port=REDIS_PORT,
    db=REDIS_DATABASE,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True,
)

pg_conn = psycopg2.connect(
    host=POSTGRES_HOSTNAME,
    port=POSTGRES_PORT,
    dbname=POSTGRES_DATABASE,
    user=POSTGRES_USERNAME,
    password=POSTGRES_PASSWORD,
)

pg_cur = pg_conn.cursor()

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


def GetUserByID(user_id: str):
    pg_cur.execute(
        SQL("SELECT * FROM users WHERE id = %s"),
        (user_id,),
    )

    user = pg_cur.fetchone()

    if user:
        (user_id, display_name, username, password_hash) = user

        return User(
            id=user_id,
            display_name=display_name,
            username=username,
            password_hash=password_hash,
        )


def GetToken(user_id: str):
    return rd.get(f"user:{user_id}:token")


def SetToken(user_id: str):
    token = GenerateToken()
    rd_key = f"user:{user_id}:token"
    rd.set(rd_key, token)
    rd.expire(rd_key, 60 * 60 * 24 * 30)

    return token


def RemoveToken(user_id: str):
    rd_key = f"user:{user_id}:token"

    if not rd.get(rd_key):
        return False

    rd.delete(rd_key)

    return True
