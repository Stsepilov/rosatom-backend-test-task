from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True, default=None)
    username: str = Field(unique=True, index=True, default=None)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_moderator: bool = Field(default=False)
