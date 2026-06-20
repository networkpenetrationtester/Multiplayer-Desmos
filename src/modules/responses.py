from enum import Enum

from src.modules.objects import APIResonse


class FAILURE_CODES(Enum):
    GENERAL = 0
    USERNAME_VOID = 1
    USERNAME_EXISTS = 2
    USERNAME_INVALID = 3
    EMAIL_VOID = 4
    EMAIL_EXISTS = 5
    EMAIL_INVALID = 6
    PASSWORD_INVALID = 7
    GRAPH_VOID = 8
    GRAPH_EXISTS = 9
    GRAPH_INVALID = 10


class CreateUserResponse(APIResonse):
    auth_token: str
    refresh_token: str


class ReadUserResponse(APIResonse):
    auth_token: str
    refresh_token: str


class UpdateUserResponse(APIResonse):
    pass


class DeleteUserResponse(APIResonse):
    pass


class CreateRoomResponse(APIResonse):
    pass


class ReadRoomsResponse(APIResonse):
    pass


class UpdateRoomResponse(APIResonse):
    pass


class DeleteRoomResponse(APIResonse):
    pass


class CreateGraphResponse(APIResonse):
    pass


class ReadGraphsResponse(APIResonse):
    pass


class UpdateGraphResponse(APIResonse):
    pass


class DeleteGraphResponse(APIResonse):
    pass
