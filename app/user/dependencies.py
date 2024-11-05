from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.crud import get_user_by_username
from app.database import get_session
from app.user.models import User
from app.config import settings
from jose import jwt, JWTError


def get_current_user(token: str, session: Session = Depends(get_session)) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        user = get_user_by_username(session, username)
        if user is None:
            return None
        return user
    except JWTError:
        return None


def get_current_moderator(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user
