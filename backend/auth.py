from fastapi import HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import requests
import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime

async def exchange_session_id(session_id: str, db: AsyncIOMotorDatabase) -> dict:
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
        user_doc = await db.users.find_one({"email": data['email']}, {"_id": 0})
        
        if not user_doc:
            # Create new user with custom user_id
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user_data = {
                "user_id": user_id,
                "email": data['email'],
                "name": data['name'],
                "picture": data.get('picture'),
                "created_at": datetime.now(timezone.utc)
            }
            await db.users.insert_one(user_data)
            user = User(**user_data)
        else:
            # Update existing user info
            await db.users.update_one(
                {"email": data['email']},
                {"$set": {
                    "name": data['name'],
                    "picture": data.get('picture')
                }}
            )
            user_doc['created_at'] = user_doc['created_at'] if isinstance(user_doc['created_at'], datetime) else datetime.fromisoformat(user_doc['created_at'])
            user = User(**user_doc)
        
        # Store session_token with 7 days expiry
        session_token = data['session_token']
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session_data = {
            "user_id": user.user_id,
            "session_token": session_token,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        }
        await db.user_sessions.insert_one(session_data)
        
        return {
            "user": user.model_dump(mode='json'),
            "session_token": session_token
        }
        
    except requests.RequestException as e:
        logger.error(f"Error exchanging session_id: {e}")
        raise HTTPException(status_code=500, detail="Authentication service error")

async def get_current_user(request: Request, db: AsyncIOMotorDatabase) -> User:
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
    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry
    expires_at = session_doc['expires_at']
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        await db.user_sessions.delete_one({"session_token": session_token})
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user_doc = await db.users.find_one(
        {"user_id": session_doc['user_id']},
        {"_id": 0}
    )
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user_doc['created_at'], str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return User(**user_doc)

async def logout_user(session_token: str, db: AsyncIOMotorDatabase):
    """Delete user session"""
    await db.user_sessions.delete_one({"session_token": session_token})