from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import RedirectResponse
from urllib.parse import urlencode
from sqlmodel import Session, select
import httpx, os 
from jose import JWTError, jwt
from datetime import datetime, timedelta

from App.database import get_session
from App.models import Customers
from App.settings import settings

# --- Router Setup ---
router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Google OAuth2 Config ---
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"

# --- JWT Secret (store securely in .env ideally) ---
JWT_SECRET = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.ALGORITHM
JWT_EXPIRY_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# --- 1️⃣ Google Login Route ---
@router.get("/login")
async def login():
    query_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(query_params)}"
    return RedirectResponse(url)


# --- 2️⃣ Google Callback Route ---
@router.get("/callback")
async def callback(request: Request, session: Session = Depends(get_session)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")

    # --- Exchange code for tokens ---
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
        token_response.raise_for_status()
        tokens = token_response.json()

        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token not found")

        # --- Get user info ---
        userinfo_response = await client.get(
            GOOGLE_USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

    google_id = user_info.get("id")
    name = user_info.get("name")

    if not google_id:
        raise HTTPException(status_code=400, detail="Invalid user info from Google")

    # --- Check if user exists ---
    existing_user = session.exec(select(Customers).where(Customers.google_id == google_id)).first()

    if not existing_user:
        # Create new user
        new_user = Customers(google_id=google_id, name=name)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        user = new_user
    else:
        user = existing_user

    # --- Generate JWT token ---
    payload = {
        "sub": str(user.id),
        "google_id": user.google_id,
        "name": user.name,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {"access_token": token, "token_type": "bearer", "user": user_info}


# --- 3️⃣ Optional route for testing protected endpoints ---
@router.get("/me")
def get_user_info(token: str):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"decoded_user": decoded}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
