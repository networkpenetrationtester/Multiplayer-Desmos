from os import environ
from os.path import dirname, exists, join

from dotenv import load_dotenv

config_path = join(dirname(__file__), "../../config/")

if not environ.get("IS_DOCKER") == "true":
    extern_env_path = join(config_path, "external.env")
    if exists(extern_env_path):
        load_dotenv(dotenv_path=extern_env_path)


REDIS_HOSTNAME = environ.get("REDIS_HOSTNAME") or ""
REDIS_DATABASE = int(environ.get("REDIS_DATABASE") or "")
REDIS_USERNAME = environ.get("REDIS_USERNAME") or ""
REDIS_PASSWORD = environ.get("REDIS_PASSWORD") or ""
REDIS_PORT = int(environ.get("REDIS_PORT") or "")

POSTGRES_HOSTNAME = environ.get("POSTGRES_HOSTNAME") or ""
POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE") or ""
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME") or ""
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD") or ""
POSTGRES_PORT = int(environ.get("POSTGRES_PORT") or "")
