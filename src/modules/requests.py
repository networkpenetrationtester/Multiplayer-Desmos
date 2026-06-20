from pydantic import BaseModel
from src.modules.objects import Room


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UpdateUserRequest(BaseModel):
    pass


class DeleteUserRequest(BaseModel):
    pass


class CreateRoomRequest(BaseModel):  # TODO: workers that clean up rooms with 0 players
    name: str
    hidden: bool
    auth_required: bool
    password: str | None


class ReadRoomsRequest(BaseModel):
    include_passworded: bool
    include_auth_required: bool


class UpdateRoomRequest(BaseModel):
    id: str
    name: str
    password: str | None = None
    hidden: bool
    auth_required: bool


class DeleteRoomRequest(BaseModel):
    id: str


class CreateGraphRequest(BaseModel):
    name: str
    # expressions: array


class ReadGraphsRequest(BaseModel):
    query: str | None
    collection: str
    count: int | None
    offset: int | None


class UpdateGraphRequest(BaseModel):
    id: str
    # content: str


class DeleteGraphRequest(BaseModel):
    id: str
