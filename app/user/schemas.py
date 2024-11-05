from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    moderator: bool


class UserLogin(BaseModel):
    username: str
    password: str
