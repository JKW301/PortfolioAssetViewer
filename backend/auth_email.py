from fastapi import HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
import logging
import bcrypt
import secrets
from database import User as DBUser, UserSession as DBUserSession

logger = logging.getLogger(__name__)

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

async def create_user(signup_data: UserSignup, db: AsyncSession) -> User:
    """Create a new user with email and password"""
    # Check if user already exists
    result = await db.execute(select(DBUser).where(DBUser.email == signup_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    password_hash = hash_password(signup_data.password)
    
    new_user = DBUser(
        user_id=user_id,
        email=signup_data.email,
        name=signup_data.name,
        password_hash=password_hash,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return User(
        user_id=new_user.user_id,
        email=new_user.email,
        name=new_user.name,
        picture=new_user.picture,
        created_at=new_user.created_at
    )

async def authenticate_user(login_data: UserLogin, db: AsyncSession) -> dict:
    """Authenticate user with email and password"""
    # Find user by email
    result = await db.execute(select(DBUser).where(DBUser.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create session token
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session = DBUserSession(
        user_id=user.user_id,
        session_token=session_token,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(session)
    await db.commit()
    
    return {
        "user": User(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            picture=user.picture,
            created_at=user.created_at
        ).model_dump(),
        "session_token": session_token
    }

async def get_current_user(request: Request, db: AsyncSession) -> User:
    """Get current user from session_token (cookie or header)"""
    # Try cookie first
    session_token = request.cookies.get('session_token')
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header.replace('Bearer ', '')
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find session
    result = await db.execute(
        select(DBUserSession).where(DBUserSession.session_token == session_token)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        await db.delete(session)
        await db.commit()
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    result = await db.execute(
        select(DBUser).where(DBUser.user_id == session.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fix timezone issue for created_at
    created_at = user.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    return User(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        created_at=created_at
    )

async def logout_user(session_token: str, db: AsyncSession):
    """Delete user session"""
    result = await db.execute(
        select(DBUserSession).where(DBUserSession.session_token == session_token)
    )
    session = result.scalar_one_or_none()
    
    if session:
        await db.delete(session)
        await db.commit()