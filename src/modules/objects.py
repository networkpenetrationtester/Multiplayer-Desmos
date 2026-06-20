from pydantic import BaseModel


class User(BaseModel):
    id: str
    display_name: str | None = None
    username: str
    password_hash: str


class Room(BaseModel):
    id: str
    name: str
    password_hash: str | None = None
    hidden: bool
    auth_required: bool


class Graph(BaseModel):
    id: str
    owner_id: str
    name: str
    # content: array
    private: bool


class APIResonse(BaseModel):
    success: bool
    message: str | None = None
    data: dict = {}
