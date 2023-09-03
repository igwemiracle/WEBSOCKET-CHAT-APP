from pydantic import BaseModel
from typing import Union, Optional


class BaseUser(BaseModel):
    username: str
    email: Optional[str] = None


class UserCreate(BaseUser):
    password: Union[str, int] = None


class Token(BaseModel):
    access_token: str
    token_type: str
