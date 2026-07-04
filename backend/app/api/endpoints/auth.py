from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, create_email_token, decode_token
)
from app.models.models import User, Subscription
from app.schemas.schemas import (
    UserRegister, UserLogin, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest, UserResponse
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_or_create_subscription(db: Session, user_id: int):
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not sub:
        sub = Subscription(user_id=user_id, plan_type="free", status="active")
        db.add(sub)
        db.commit()
    return sub


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed_pw = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        name=user_in.name,
        is_verified=True,   # Auto-verify for local dev; set False for email flow
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _get_or_create_subscription(db, user.id)

    verification_token = create_email_token(user.id)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

    return {
        "message": "Registration successful! Check your email to verify your account.",
        "user_id": user.id,
        "verify_url": verify_url,   # Shown in dev; in prod send via email
    }


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    _get_or_create_subscription(db, user.id)
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

    new_access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "email":
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully! You can now log in."}


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    # Always return success to prevent email enumeration attacks
    if user:
        reset_token = create_email_token(user.id, expires_hours=1)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        # In production, send this via email
        print(f"[DEV] Password reset URL for {user.email}: {reset_url}")
    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    payload = decode_token(request.token)
    if not payload or payload.get("type") != "email":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Password reset successfully!"}


@router.get("/google/login")
def google_login():
    """Returns the Google OAuth2 authorization URL."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google OAuth not configured.")
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    import urllib.parse
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return {"auth_url": auth_url}


@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    """Exchanges Google auth code for tokens and logs the user in."""
    import httpx
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_resp = httpx.post(token_url, data=data)
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch Google token.")

    id_token = token_resp.json().get("id_token")
    # Decode Google JWT (unverified for simplicity; use google-auth lib in prod)
    import base64, json as _json
    try:
        payload_b64 = id_token.split(".")[1]
        padding = 4 - len(payload_b64) % 4
        profile = _json.loads(base64.urlsafe_b64decode(payload_b64 + "=" * padding))
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decode Google token.")

    email = profile.get("email")
    name = profile.get("name", email)
    google_id = profile.get("sub")
    picture = profile.get("picture")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name, google_id=google_id,
                    profile_picture_url=picture, is_verified=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        _get_or_create_subscription(db, user.id)
    elif not user.google_id:
        user.google_id = google_id
        db.commit()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    # Redirect to frontend with tokens
    from fastapi.responses import RedirectResponse
    redirect_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(url=redirect_url)
