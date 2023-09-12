import jwt
from jwt.exceptions import DecodeError
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from starlette.config import Config
from ..Database.connection import SECRET_KEY


config = Config(".env")
# algorithms = config.get("ALGORITHM")


def create_access_token(username: str, password: str) -> str:
    payload = {
        "username": username,
        "password": password,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY,
                       algorithm="HS256")
    return token


def verify_access_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, SECRET_KEY, algorithms="HS256")
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except DecodeError as e:
        print("JWT Decode Error:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
