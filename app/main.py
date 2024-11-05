from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from .database import create_db_and_tables, get_session
from .message.models import Message
from .user.dependencies import get_current_moderator, get_current_user
from .user.models import User
from .user.schemas import UserCreate, UserLogin
from .message.schemas import MessageCreate
from .crud import create_user, get_user_by_username, create_message, get_all_message, get_message, delete_user
from app.user.auth import verify_password, create_access_token
from .websocket import ConnectionManager
from typing import List


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
manager = ConnectionManager()


@app.post("/register", response_model=User)
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = get_user_by_username(session, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return create_user(session, user.username, user.password, user.moderator)


@app.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = get_user_by_username(session, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.id}


@app.post("/messages", response_model=Message)
def send_message(message: MessageCreate, session: Session = Depends(get_session)):
    return create_message(session, message.content, message.sender_id, message.channel_id)


@app.get("/messages/{username}/{channel_id}", response_model=List[Message])
def get_messages(username: str, channel_id: int, session: Session = Depends(get_session)):
    return get_message(session, get_user_by_username(session, username).id, channel_id)


@app.delete("/admin/users/{user_id}")
def delete_user_moderator(user_id: int, moderator: User = Depends(get_current_moderator),
                          session: Session = Depends(get_session)):
    delete_user(session, user_id)
    return {"message": "User deleted"}


@app.websocket("/ws/chat/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: int, session: Session = Depends(get_session)):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    user_id = get_current_user(token, session).id
    if user_id is None:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = create_message(session, data, sender_id=user_id, channel_id=channel_id)
            await manager.broadcast(f"[Channel {channel_id}] User {user_id}: {message.content}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Client disconnected")


@app.get("/admin/messages", response_model=List[Message])
def get_all_messages(moderator: User = Depends(get_current_moderator), session: Session = Depends(get_session)):
    return get_all_message(session)
