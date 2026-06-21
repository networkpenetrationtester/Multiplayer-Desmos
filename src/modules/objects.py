from pydantic.dataclasses import dataclass


@dataclass
class User:
    id: str
    username: str
    password_hash: str
    display_name: str | None = None


@dataclass
class Room:
    id: str
    name: str
    hidden: bool
    auth_required: bool
    password_hash: str | None = None


@dataclass
class Graph:
    id: str
    owner_id: str
    name: str
    # content: array
    private: bool
