from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True, default=None)
    content: str
    sender_id: int
    channel_id: int
