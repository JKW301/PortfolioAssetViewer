"""
Migration: Add password_hash column to users table
This migration adds support for email/password authentication
"""
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def migrate():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not set")
        return
    
    # Convert to async driver
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)
    elif DATABASE_URL.startswith('postgresql://') and 'asyncpg' not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Check if column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='password_hash'
        """)
        result = await conn.execute(check_query)
        exists = result.scalar_one_or_none()
        
        if exists:
            print("✅ Column 'password_hash' already exists")
        else:
            # Add the column
            alter_query = text("""
                ALTER TABLE users 
                ADD COLUMN password_hash VARCHAR(255) NULL
            """)
            await conn.execute(alter_query)
            print("✅ Added 'password_hash' column to users table")
    
    await engine.dispose()
    print("✅ Migration completed successfully")

if __name__ == "__main__":
    asyncio.run(migrate())
