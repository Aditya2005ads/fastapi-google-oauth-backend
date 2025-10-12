from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlmodel import Session, select
from typing import Optional

from App.settings import settings
from App.database import get_session
from App.models import Customers


security = HTTPBearer(auto_error=True)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> Customers:
    """Extract current user from Bearer token and fetch from DB."""
    if creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    payload = decode_token(creds.credentials)
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = session.exec(select(Customers).where(Customers.id == int(user_id))).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
