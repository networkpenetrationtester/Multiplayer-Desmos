from enum import Enum

from pydantic import BaseModel
from typing_extensions import Any


class APIResonse(BaseModel):
    success: bool
    message: str | None = None
    data: dict[str, Any] | None = None


class FAILURE_CODES(Enum):
    GENERAL = 0
    USER_VOID = 1
    USER_EXISTS = 2
    USER_INVALID = 3
    # EMAIL_VOID = 4
    # EMAIL_EXISTS = 5
    # EMAIL_INVALID = 6
    PASSWORD_INVALID = 7
    GRAPH_VOID = 8
    GRAPH_EXISTS = 9
    GRAPH_INVALID = 10
    TOKEN_VOID = 11
    TOKEN_INVALID = 12


def APIResponse(
    success: bool,
    failure_code: FAILURE_CODES | None = None,
    message: str | None = None,
    data: dict[str, Any] | None = None,
):

    _dict = dict()
    _dict["success"] = success
    if failure_code:
        _dict["failure_code"] = failure_code
    if message:
        _dict["message"] = message
    if data:
        _dict["data"] = data

    return _dict
