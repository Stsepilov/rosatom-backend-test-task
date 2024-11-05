from typing import Optional, List, Sequence, Type

from fastapi import HTTPException
from sqlmodel import Session, select, delete

from app.user.auth import get_password_hash
from .message.models import Message
from .user.models import User


def create_user(session: Session, username: str, password: str, moderator: bool = False) -> User:
    hashed_password = get_password_hash(password)
    user = User(username=username, hashed_password=hashed_password, is_moderator=moderator)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def create_message(session: Session, content: str, sender_id: int, channel_id: int) -> Message:
    message = Message(content=content, sender_id=sender_id, channel_id=channel_id)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def get_message(session: Session, sender_id: int, channel_id: int) -> List[Message]:
    messages = session.exec(
        select(Message).where(Message.sender_id == sender_id, Message.channel_id == channel_id)).all()
    if len(messages) == 0:
        raise HTTPException(status_code=404, detail="Messages not Found")
    return list(messages)


def get_all_message(session: Session) -> List[Message]:
    messages = session.exec(select(Message)).all()
    return list(messages)


def delete_user(session: Session, user_id: int) -> User:
    user = session.exec(select(User).where(User.id == user_id)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    session.exec(delete(User).where(User.id == user_id))
    session.commit()
    return user
