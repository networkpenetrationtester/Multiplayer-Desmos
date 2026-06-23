import re
from hashlib import sha256
from secrets import SystemRandom

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

ph = PasswordHasher()


def FailWithMessage(message: str):
    return {"pass": False, "message": message}


def ValidateUsername(username: str):
    if len(username) > 16:
        return FailWithMessage("Username too long (16 max).")

    if len(username) < 2:
        return FailWithMessage("Username too short (2 min).")

    try:  # disallow special char as first char
        if [" ", "_", "."].index(username[0]) != 0:
            return FailWithMessage("Username may not begin with special character.")
    except ValueError:
        pass  # string did not contain a special character at first position
    pat = re.compile(
        r"^[aA0-zZ9._ ]{2,16}$"  # this is exclusive, the match must go from beginning to end.
    )  # only allow 2-16 alphanumeric, space, period, underscore
    mat = pat.match(username)
    if not mat:
        return FailWithMessage(
            "Username may only contain alphanumerical, space, period, and underscore characters."
        )

    return {"pass": True, "message": None}


def ValidatePassword(password: str):
    if len(password) > 32:
        return FailWithMessage("Password too long (32 max).")

    if len(password) < 8:
        return FailWithMessage("Password too short (8 min).")

    if not re.compile(r"[~`!@#$%^&*()_+{}|:\"<>?\-=[\]\\;',./]").search(password):
        return FailWithMessage("Password must contain a special character.")

    if not re.compile(r"[A-Z]").search(password):
        return FailWithMessage("Password must contain an uppercase character.")

    if not re.compile(r"[a-z]").search(password):
        return FailWithMessage("Password must contain a lowercase character.")

    if not re.compile(r"[0-9]").search(password):
        return FailWithMessage("Password must contain a number.")

    return {"pass": True, "message": None}


def ArgonHash(password: str):
    return ph.hash(password)


def GenerateToken():
    return sha256(string=str(SystemRandom().getrandbits(256)).encode()).hexdigest()


def CheckPassword(password_hash: str, password: str):
    try:
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except VerificationError:
        return False
    except InvalidHashError:
        return False
