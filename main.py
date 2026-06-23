from random import randint

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from ulid import ULID

from src.modules.database import (
    AddUser,
    GetToken,
    GetUserByID,
    GetUserByUsername,
    RemoveToken,
    SetToken,
)
from src.modules.objects import User
from src.modules.requests import LoginRequest, LogoutRequest, RegisterRequest
from src.modules.responses import FAILURE_CODES, APIResponse
from src.modules.stateless import (
    ArgonHash,
    CheckPassword,
    ValidatePassword,
    ValidateUsername,
)

# TODO: ENV VARIABLES
# redis keys: room:<roomid> -> { content: { expression: <expr>, owner: <userid> }[] }
# redis keys: user:<user_id>:token -> <token>
#


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def _root():
    return open("src/www/index.html").read()


@app.post("/api/register", response_class=JSONResponse)
async def _register(request: RegisterRequest):  # TODO: APIResponse maker thing
    valid_username = ValidateUsername(request.username)

    if not valid_username["pass"]:
        return APIResponse(
            success=False,
            failure_code=FAILURE_CODES.USER_INVALID,
            message=valid_username["message"],
        )

    valid_password = ValidatePassword(request.password)

    if not valid_password["pass"]:
        return APIResponse(
            success=False,
            failure_code=FAILURE_CODES.PASSWORD_INVALID,
            message=valid_password["message"],
        )

    new_user = AddUser(
        User(
            id=str(ULID()),
            username=request.username,
            password_hash=ArgonHash(request.password),
        )
    )

    if not new_user:
        return APIResponse(
            success=False,
            failure_code=FAILURE_CODES.USER_EXISTS,
            message="That user already exists.",
        )

    token = SetToken(new_user.id)

    return APIResponse(success=True, data={"token": token, "id": new_user.id})


@app.post("/api/login", response_class=JSONResponse)
async def _login(request: LoginRequest):
    user = GetUserByUsername(request.username)

    if not user:
        return APIResponse(
            success=False,
            failure_code=FAILURE_CODES.USER_VOID,
            message="That user does not exist.",
        )

    if not CheckPassword(user.password_hash, request.password):
        return APIResponse(
            success=False,
            failure_code=FAILURE_CODES.PASSWORD_INVALID,
            message="That password is incorrect.",
        )

    token = GetToken(user.id) or SetToken(user.id)

    return APIResponse(success=True, data={"token": token, "id": user.id})


# BEARER, BODY REQUIRES USER ID BECAUSE IM FUCKING LAZY AND REDIS IS SLOW
@app.post("/api/logout", response_class=JSONResponse)
async def _logout(request: Request):
    bearer = request.headers.get("authorization")

    if not bearer:
        return APIResponse(
            success=False,
            failure_code=FAILURE_CODES.TOKEN_INVALID,
            message="Bearer token missing or invalid (Form: Bearer <token>).",
        )

    bearer = bearer.split("Bearer ")[1]
    dict = await request.json()

    try:
        logout_request = LogoutRequest(**dict)

        user_id = logout_request.user_id

        if not GetUserByID(user_id):
            return APIResponse(
                success=False,
                failure_code=FAILURE_CODES.USER_VOID,
                message="User does not exist.",
            )

        token = GetToken(user_id)

        if not token:
            return APIResponse(
                success=False,
                failure_code=FAILURE_CODES.TOKEN_VOID,
                message="Token does not exist.",
            )

        if not bearer == token:
            return APIResponse(
                success=False,
                failure_code=FAILURE_CODES.TOKEN_INVALID,
                message="User ID and token unrelated.",
            )

        if not RemoveToken(user_id):
            return APIResponse(
                success=False,
                failure_code=FAILURE_CODES.GENERAL,
                message="Failed to find user token in redis.",
            )

        return APIResponse(success=True, message="Successfully logged out.")

    except ValidationError:
        return APIResponse(
            success=False,
            failure_code=FAILURE_CODES.GENERAL,
            message="Malformed input, only required field is user_id.",
        )


@app.get("/api/counts", response_class=JSONResponse)
def _counts():
    return {"2d": randint(0, 1000), "3d": randint(0, 1000)}


app.mount("/", StaticFiles(directory="src/www"))
