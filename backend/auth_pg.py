from fastapi import HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import requests
import uuid
from pydantic import BaseModel
from typing import Optional
import logging
from database import User as DBUser, UserSession as DBUserSession

logger = logging.getLogger(__name__)

class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

async def exchange_session_id(session_id: str, db: AsyncSession) -> dict:
    """Exchange session_id for user data and session_token from Emergent Auth"""
    try:
        response = requests.get(
            'https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data',
            headers={'X-Session-ID': session_id},
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session_id")
        
        data = response.json()
        
        # Check if user exists
        result = await db.execute(
            select(DBUser).where(DBUser.email == data['email'])
        )
        user_db = result.scalar_one_or_none()
        
        if not user_db:
            # Create new user
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user_db = DBUser(
                user_id=user_id,
                email=data['email'],
                name=data['name'],
                picture=data.get('picture')
            )
            db.add(user_db)
            await db.commit()
            await db.refresh(user_db)
        else:
            # Update existing user info
            user_db.name = data['name']
            user_db.picture = data.get('picture')
            await db.commit()
        
        user = User.model_validate(user_db)
        
        # Store session_token
        session_token = data['session_token']
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session_db = DBUserSession(
            user_id=user.user_id,
            session_token=session_token,
            expires_at=expires_at
        )
        db.add(session_db)
        await db.commit()
        
        return {
            "user": user.model_dump(),
            "session_token": session_token
        }
        
    except requests.RequestException as e:
        logger.error(f"Error exchanging session_id: {e}")
        raise HTTPException(status_code=500, detail="Authentication service error")

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
    session_db = result.scalar_one_or_none()
    
    if not session_db:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry
    if session_db.expires_at < datetime.now(timezone.utc):
        await db.delete(session_db)
        await db.commit()
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    result = await db.execute(
        select(DBUser).where(DBUser.user_id == session_db.user_id)
    )
    user_db = result.scalar_one_or_none()
    
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User.model_validate(user_db)

async def logout_user(session_token: str, db: AsyncSession):
    """Delete user session"""
    result = await db.execute(
        select(DBUserSession).where(DBUserSession.session_token == session_token)
    )
    session_db = result.scalar_one_or_none()
    if session_db:
        await db.delete(session_db)
        await db.commit()
