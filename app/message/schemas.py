from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str
    sender_id: int
    channel_id: int

