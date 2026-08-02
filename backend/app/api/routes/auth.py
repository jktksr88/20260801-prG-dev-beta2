from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
import jwt
from app.database.session import get_db
from app.models import User, RefreshToken
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserResponse
from app.auth.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, token_digest
from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.services.rate_limit import limit_auth

router=APIRouter(prefix="/auth",tags=["authentication"])

def issue_tokens(db: Session,user: User) -> TokenResponse:
    access=create_access_token(user.id); refresh=create_refresh_token(user.id)
    db.add(RefreshToken(user_id=user.id,token_hash=token_digest(refresh),expires_at=datetime.now(timezone.utc)+timedelta(days=settings.refresh_token_days)))
    db.commit()
    return TokenResponse(access_token=access,refresh_token=refresh)

@router.post("/register",response_model=TokenResponse,status_code=201)
def register(payload:RegisterRequest,request:Request,db:Session=Depends(get_db)):
    limit_auth(request)
    email=payload.email.lower()
    if db.scalar(select(User).where(User.email==email)):
        raise HTTPException(409,"An account with this email already exists")
    try: password_hash=hash_password(payload.password)
    except ValueError as exc: raise HTTPException(422,str(exc))
    user=User(email=email,password_hash=password_hash,preferred_language=payload.preferred_language)
    db.add(user); db.commit(); db.refresh(user)
    return issue_tokens(db,user)

@router.post("/login",response_model=TokenResponse)
def login(payload:LoginRequest,request:Request,db:Session=Depends(get_db)):
    limit_auth(request)
    user=db.scalar(select(User).where(User.email==payload.email.lower()))
    if not user or not verify_password(payload.password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect email or password")
    return issue_tokens(db,user)

@router.post("/refresh",response_model=TokenResponse)
def refresh(payload:RefreshRequest,request:Request,db:Session=Depends(get_db)):
    limit_auth(request)
    try: decoded=decode_token(payload.refresh_token,"refresh")
    except jwt.PyJWTError: raise HTTPException(401,"Invalid or expired refresh token")
    token=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==token_digest(payload.refresh_token),RefreshToken.revoked.is_(False)))
    now=datetime.now(timezone.utc)
    if not token or token.expires_at.replace(tzinfo=timezone.utc) <= now:
        raise HTTPException(401,"Refresh token is no longer valid")
    token.revoked=True; db.commit()
    user=db.get(User,decoded["sub"])
    if not user: raise HTTPException(401,"User not found")
    return issue_tokens(db,user)

@router.get("/me",response_model=UserResponse)
def me(user:User=Depends(get_current_user)): return user

@router.post("/logout",status_code=204)
def logout(payload:RefreshRequest,db:Session=Depends(get_db)):
    token=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==token_digest(payload.refresh_token)))
    if token: token.revoked=True; db.commit()

@router.delete("/account",status_code=204)
def delete_account(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    db.delete(user); db.commit()
