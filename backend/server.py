from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables before importing other modules
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from binance.client import Client
import urllib.parse
import secrets

from database import (
    get_db, init_db,
    CryptoAsset as DBCryptoAsset,
    StockAsset as DBStockAsset,
    CoinAsset as DBCoinAsset,
    HistorySnapshot as DBHistorySnapshot,
    User as DBUser,
    UserSession as DBUserSession
)
from auth_pg import exchange_session_id, logout_user as logout_user_pg
from auth_email import (
    create_user, authenticate_user, get_current_user, logout_user,
    UserSignup, UserLogin, User
)

# Try multiple possible locations for frontend build
possible_paths = [
    Path("/opt/render/project/src/frontend/build"),  # Render path
    Path("/app/frontend/build"),  # Docker/Heroku path
    ROOT_DIR.parent / "frontend" / "build",  # Relative to backend
    Path("../frontend/build"),  # Relative path
    Path("./frontend/build"),  # Current directory
    Path("frontend/build"),  # Simple relative
]

FRONTEND_BUILD = None
for path in possible_paths:
    if path.exists() and (path / "index.html").exists():
        FRONTEND_BUILD = path
        break

binance_api_key = os.environ.get('BINANCE_API_KEY', 'BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia')
binance_client = None

def get_binance_client():
    global binance_client
    if binance_client is None:
        try:
            binance_client = Client(binance_api_key, '', testnet=False)
        except Exception as e:
            binance_client = False
    return binance_client if binance_client is not False else None

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Pydantic models
class SessionIdRequest(BaseModel):
    session_id: str

class CryptoAssetCreate(BaseModel):
    name: str
    symbol: str
    quantity: float
    purchase_price: float

class CryptoAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    symbol: str
    quantity: float
    purchase_price: float
    created_at: datetime

class StockAssetCreate(BaseModel):
    name: str
    symbol: str
    quantity: float
    purchase_price: float

class StockAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    symbol: str
    quantity: float
    purchase_price: float
    created_at: datetime

class CoinAssetCreate(BaseModel):
    name: str
    url: str
    css_selector: str
    quantity: float

class CoinAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    url: str
    css_selector: str
    quantity: float
    created_at: datetime

class HistorySnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    timestamp: datetime
    total_value_eur: float
    crypto_value_eur: float
    stocks_value_eur: float
    coins_value_eur: float

# Helper functions
def get_eur_usd_rate():
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        return response.json()['rates']['EUR']
    except:
        return 0.92

async def get_crypto_price_eur(symbol: str) -> Optional[float]:
    try:
        client = get_binance_client()
        if client is None:
            return None
        ticker = client.get_symbol_ticker(symbol=f"{symbol.upper()}USDT")
        usd_price = float(ticker['price'])
        return usd_price * get_eur_usd_rate()
    except:
        return None

async def get_stock_price_eur(symbol: str) -> Optional[float]:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d')
        if not hist.empty:
            return hist['Close'].iloc[-1] * get_eur_usd_rate()
        return None
    except:
        return None

async def get_coin_price_eur(url: str, css_selector: str) -> Optional[float]:
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        element = soup.select_one(css_selector)
        if element:
            import re
            price_text = element.get_text().strip().replace('€', '').replace(',', '.').replace(' ', '')
            match = re.search(r'(\d+\.?\d*)', price_text)
            if match:
                return float(match.group(1))
        return None
    except:
        return None

# Auth routes
@api_router.post("/auth/signup")
async def signup(signup_data: UserSignup, response: Response, db: AsyncSession = Depends(get_db)):
    """Create a new user account"""
    try:
        user = await create_user(signup_data, db)
        # Automatically log in the new user
        login_data = UserLogin(email=signup_data.email, password=signup_data.password)
        result = await authenticate_user(login_data, db)
        
        response.set_cookie(
            key="session_token", 
            value=result['session_token'], 
            httponly=True, 
            secure=True, 
            samesite="none", 
            max_age=7*24*60*60, 
            path="/"
        )
        
        return {"user": result["user"], "message": "Account created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/auth/login")
async def login(login_data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    """Login with email and password"""
    try:
        result = await authenticate_user(login_data, db)
        
        response.set_cookie(
            key="session_token", 
            value=result['session_token'], 
            httponly=True, 
            secure=True, 
            samesite="none", 
            max_age=7*24*60*60, 
            path="/"
        )
        
        return {"user": result["user"], "message": "Login successful"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@api_router.get("/auth/login")
async def login_old(request: Request):
    """Provide Google OAuth login URL (legacy endpoint)"""
    # First try the Emergent Auth service 
    emergent_urls = [
        "https://demobackend.emergentagent.com/auth/v1/oauth/google",
        "https://demobackend.emergentagent.com/auth/oauth/google"
    ]
    
    # For development/fallback, create a direct Google OAuth URL
    # Note: You'd need to set GOOGLE_CLIENT_ID in environment for production
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    base_url = str(request.base_url).rstrip('/')
    redirect_uri = f"{base_url}/api/auth/callback"
    
    if google_client_id:
        # Direct Google OAuth
        google_auth_url = (
            f"https://accounts.google.com/oauth2/auth?"
            f"client_id={google_client_id}&"
            f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
            f"scope=email profile&"
            f"response_type=code&"
            f"state={secrets.token_urlsafe(32)}"
        )
        
        return {
            "auth_url": google_auth_url,
            "method": "direct_google_oauth",
            "redirect_uri": redirect_uri
        }
    else:
        # Try Emergent Auth (may not work)
        return {
            "auth_url": emergent_urls[0],
            "method": "emergent_auth",
            "message": "Using Emergent Auth service - may need Google OAuth setup if this fails",
            "setup_instructions": "Set GOOGLE_CLIENT_ID environment variable for direct Google OAuth"
        }

@api_router.post("/auth/logout")
async def logout_route(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """Logout current user"""
    session_token = request.cookies.get('session_token')
    if session_token:
        await logout_user(session_token, db)
        response.delete_cookie("session_token", path="/")
    return {"message": "Logged out successfully"}

@api_router.get("/auth/me")
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    """Get current user information"""
    current_user = await get_current_user(request, db)
    return current_user.model_dump()

@api_router.get("/auth/callback")
async def auth_callback(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """Handle OAuth callback"""
    session_id = request.query_params.get('session_id')
    code = request.query_params.get('code')  # Google OAuth code
    
    if session_id:
        # Emergent Auth flow
        try:
            result = await exchange_session_id(session_id, db)
            response.set_cookie(
                key="session_token", 
                value=result['session_token'], 
                httponly=True, 
                secure=True, 
                samesite="none", 
                max_age=7*24*60*60, 
                path="/"
            )
            return HTMLResponse("""
                <script>window.location.href = '/';</script>
                <p>Login successful, redirecting...</p>
            """)
        except Exception as e:
            return HTMLResponse(f"""
                <div style="padding: 20px; font-family: Arial;">
                    <h2>Authentication Error</h2>
                    <p>Error: {str(e)}</p>
                    <p><a href="/">Return to home</a></p>
                </div>
            """)
    
    elif code:
        # Direct Google OAuth flow (would need implementation)
        return HTMLResponse("""
            <div style="padding: 20px; font-family: Arial;">
                <h2>Google OAuth Not Fully Implemented</h2>
                <p>Received authorization code but need to complete Google OAuth flow.</p>
                <p>Need to exchange code for tokens and create user session.</p>
                <p><a href="/">Return to home</a></p>
            </div>
        """)
    
    else:
        return HTMLResponse("""
            <div style="padding: 20px; font-family: Arial;">
                <h2>Authentication Error</h2>
                <p>No session_id or authorization code received.</p>
                <p><a href="/">Return to home</a></p>
            </div>
        """)

# Add a test login for development
@api_router.post("/auth/test-login")
async def test_login(response: Response, db: AsyncSession = Depends(get_db)):
    """Create a test user session for development"""
    try:
        # Create or get test user
        result = await db.execute(
            select(DBUser).where(DBUser.email == "test@example.com")
        )
        user_db = result.scalar_one_or_none()
        
        if not user_db:
            from datetime import datetime, timezone, timedelta
            
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user_db = DBUser(
                user_id=user_id,
                email="test@example.com",
                name="Test User",
                picture=None
            )
            db.add(user_db)
            await db.commit()
            await db.refresh(user_db)
        
        # Create session
        session_token = f"test_session_{secrets.token_urlsafe(32)}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session_db = DBUserSession(
            user_id=user_db.user_id,
            session_token=session_token,
            expires_at=expires_at
        )
        db.add(session_db)
        await db.commit()
        
        response.set_cookie(
            key="session_token", 
            value=session_token, 
            httponly=True, 
            secure=True, 
            samesite="none", 
            max_age=7*24*60*60, 
            path="/"
        )
        
        user = User.model_validate(user_db)
        return {
            "message": "Test login successful",
            "user": user.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test login failed: {str(e)}")

@api_router.post("/auth/session")
async def create_session(req: SessionIdRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await exchange_session_id(req.session_id, db)
    response.set_cookie(key="session_token", value=result['session_token'], httponly=True, secure=True, samesite="none", max_age=7*24*60*60, path="/")
    return result

# Crypto endpoints
@api_router.post("/crypto", response_model=CryptoAssetResponse)
async def create_crypto(asset: CryptoAssetCreate, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    crypto = DBCryptoAsset(asset_id=str(uuid.uuid4()), user_id=current_user.user_id, **asset.model_dump())
    db.add(crypto)
    await db.commit()
    await db.refresh(crypto)
    return CryptoAssetResponse(id=crypto.asset_id, **asset.model_dump(), created_at=crypto.created_at)

@api_router.get("/crypto", response_model=List[CryptoAssetResponse])
async def get_cryptos(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    result = await db.execute(select(DBCryptoAsset).where(DBCryptoAsset.user_id == current_user.user_id))
    return [CryptoAssetResponse(id=c.asset_id, name=c.name, symbol=c.symbol, quantity=c.quantity, purchase_price=c.purchase_price, created_at=c.created_at) for c in result.scalars().all()]

@api_router.delete("/crypto/{crypto_id}")
async def delete_crypto(crypto_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    result = await db.execute(select(DBCryptoAsset).where(DBCryptoAsset.asset_id == crypto_id, DBCryptoAsset.user_id == current_user.user_id))
    crypto = result.scalar_one_or_none()
    if not crypto:
        raise HTTPException(status_code=404, detail="Crypto not found")
    await db.delete(crypto)
    await db.commit()
    return {"message": "Deleted successfully"}

@api_router.get("/crypto/{crypto_id}/price")
async def get_crypto_current_price(crypto_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    result = await db.execute(select(DBCryptoAsset).where(DBCryptoAsset.asset_id == crypto_id, DBCryptoAsset.user_id == current_user.user_id))
    crypto = result.scalar_one_or_none()
    if not crypto:
        raise HTTPException(status_code=404, detail="Crypto not found")
    price_eur = await get_crypto_price_eur(crypto.symbol)
    if price_eur is None:
        raise HTTPException(status_code=500, detail="Unable to fetch price")
    return {"symbol": crypto.symbol, "current_price_eur": price_eur, "total_value_eur": price_eur * crypto.quantity}

# Stock endpoints
@api_router.post("/stocks", response_model=StockAssetResponse)
async def create_stock(asset: StockAssetCreate, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    stock = DBStockAsset(asset_id=str(uuid.uuid4()), user_id=current_user.user_id, **asset.model_dump())
    db.add(stock)
    await db.commit()
    await db.refresh(stock)
    return StockAssetResponse(id=stock.asset_id, **asset.model_dump(), created_at=stock.created_at)

@api_router.get("/stocks", response_model=List[StockAssetResponse])
async def get_stocks(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    result = await db.execute(select(DBStockAsset).where(DBStockAsset.user_id == current_user.user_id))
    return [StockAssetResponse(id=s.asset_id, name=s.name, symbol=s.symbol, quantity=s.quantity, purchase_price=s.purchase_price, created_at=s.created_at) for s in result.scalars().all()]

@api_router.delete("/stocks/{stock_id}")
async def delete_stock(stock_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    result = await db.execute(select(DBStockAsset).where(DBStockAsset.asset_id == stock_id, DBStockAsset.user_id == current_user.user_id))
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    await db.delete(stock)
    await db.commit()
    return {"message": "Deleted successfully"}

@api_router.get("/stocks/{stock_id}/price")
async def get_stock_current_price(stock_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    result = await db.execute(select(DBStockAsset).where(DBStockAsset.asset_id == stock_id, DBStockAsset.user_id == current_user.user_id))
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    price_eur = await get_stock_price_eur(stock.symbol)
    if price_eur is None:
        raise HTTPException(status_code=500, detail="Unable to fetch price")
    return {"symbol": stock.symbol, "current_price_eur": price_eur, "total_value_eur": price_eur * stock.quantity}

# Coin endpoints
@api_router.post("/coins", response_model=CoinAssetResponse)
async def create_coin(asset: CoinAssetCreate, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    coin = DBCoinAsset(asset_id=str(uuid.uuid4()), user_id=current_user.user_id, **asset.model_dump())
    db.add(coin)
    await db.commit()
    await db.refresh(coin)
    return CoinAssetResponse(id=coin.asset_id, **asset.model_dump(), created_at=coin.created_at)

@api_router.get("/coins", response_model=List[CoinAssetResponse])
async def get_coins(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    result = await db.execute(select(DBCoinAsset).where(DBCoinAsset.user_id == current_user.user_id))
    return [CoinAssetResponse(id=c.asset_id, name=c.name, url=c.url, css_selector=c.css_selector, quantity=c.quantity, created_at=c.created_at) for c in result.scalars().all()]

@api_router.delete("/coins/{coin_id}")
async def delete_coin(coin_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    result = await db.execute(select(DBCoinAsset).where(DBCoinAsset.asset_id == coin_id, DBCoinAsset.user_id == current_user.user_id))
    coin = result.scalar_one_or_none()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    await db.delete(coin)
    await db.commit()
    return {"message": "Deleted successfully"}

@api_router.get("/coins/{coin_id}/price")
async def get_coin_current_price(coin_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    result = await db.execute(select(DBCoinAsset).where(DBCoinAsset.asset_id == coin_id, DBCoinAsset.user_id == current_user.user_id))
    coin = result.scalar_one_or_none()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    price_eur = await get_coin_price_eur(coin.url, coin.css_selector)
    if price_eur is None:
        raise HTTPException(status_code=500, detail="Unable to fetch price")
    return {"name": coin.name, "current_price_eur": price_eur, "total_value_eur": price_eur * coin.quantity}

# Portfolio overview
@api_router.get("/portfolio/overview")
async def get_portfolio_overview(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    
    crypto_result = await db.execute(select(DBCryptoAsset).where(DBCryptoAsset.user_id == current_user.user_id))
    cryptos = crypto_result.scalars().all()
    
    stock_result = await db.execute(select(DBStockAsset).where(DBStockAsset.user_id == current_user.user_id))
    stocks = stock_result.scalars().all()
    
    coin_result = await db.execute(select(DBCoinAsset).where(DBCoinAsset.user_id == current_user.user_id))
    coins = coin_result.scalars().all()
    
    crypto_value = sum([(await get_crypto_price_eur(c.symbol) or 0) * c.quantity for c in cryptos])
    stocks_value = sum([(await get_stock_price_eur(s.symbol) or 0) * s.quantity for s in stocks])
    coins_value = sum([(await get_coin_price_eur(c.url, c.css_selector) or 0) * c.quantity for c in coins])
    
    return {
        "total_value_eur": round(crypto_value + stocks_value + coins_value, 2),
        "crypto_value_eur": round(crypto_value, 2),
        "stocks_value_eur": round(stocks_value, 2),
        "coins_value_eur": round(coins_value, 2),
        "crypto_count": len(cryptos),
        "stocks_count": len(stocks),
        "coins_count": len(coins)
    }

# History endpoints
@api_router.post("/history/snapshot")
async def create_snapshot(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    overview = await get_portfolio_overview(request, db)
    
    snapshot = DBHistorySnapshot(
        snapshot_id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        total_value_eur=overview['total_value_eur'],
        crypto_value_eur=overview['crypto_value_eur'],
        stocks_value_eur=overview['stocks_value_eur'],
        coins_value_eur=overview['coins_value_eur']
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    
    return HistorySnapshotResponse(
        id=snapshot.snapshot_id,
        timestamp=snapshot.timestamp,
        total_value_eur=snapshot.total_value_eur,
        crypto_value_eur=snapshot.crypto_value_eur,
        stocks_value_eur=snapshot.stocks_value_eur,
        coins_value_eur=snapshot.coins_value_eur
    )

@api_router.get("/history/snapshots", response_model=List[HistorySnapshotResponse])
async def get_snapshots(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_current_user(request, db)
    
    result = await db.execute(
        select(DBHistorySnapshot)
        .where(DBHistorySnapshot.user_id == current_user.user_id)
        .order_by(DBHistorySnapshot.timestamp.desc())
    )
    
    return [
        HistorySnapshotResponse(
            id=s.snapshot_id,
            timestamp=s.timestamp,
            total_value_eur=s.total_value_eur,
            crypto_value_eur=s.crypto_value_eur,
            stocks_value_eur=s.stocks_value_eur,
            coins_value_eur=s.coins_value_eur
        )
        for s in result.scalars().all()
    ]

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', 'https://portfolio-tracker.onrender.com,http://localhost:3000,*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if build exists
if FRONTEND_BUILD and (FRONTEND_BUILD / "static").exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD / "static")), name="static")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    await init_db()
    if FRONTEND_BUILD:
        logger.info(f"Frontend build found at: {FRONTEND_BUILD}")
    else:
        logger.warning("Frontend build not found - serving API only")
        logger.warning(f"Working directory: {Path.cwd()}")
        logger.warning(f"ROOT_DIR: {ROOT_DIR}")
        logger.warning("Checked paths:")
        for i, path in enumerate(possible_paths):
            exists = path.exists()
            has_index = (path / "index.html").exists() if exists else False
            logger.warning(f"  {i+1}. {path} -> exists: {exists}, has_index: {has_index}")
    logger.info("Database tables created successfully")

# Serve React app
@api_router.get("/test-auth")
async def test_auth_page():
    """Serve the test authentication page"""
    test_page = ROOT_DIR / "test_auth.html"
    if test_page.exists():
        return FileResponse(test_page)
    else:
        return HTMLResponse("<h1>Test auth page not found</h1>", status_code=404)

@app.get("/")
async def root():
async def root():
    if FRONTEND_BUILD:
        index_path = FRONTEND_BUILD / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
    
    # Fallback if no build
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Tracker - Déploiement Requis</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 48px;
            max-width: 600px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        h1 { color: #1a202c; font-size: 28px; margin-bottom: 16px; }
        p { color: #4a5568; line-height: 1.6; margin-bottom: 12px; }
        .status { color: #e53e3e; font-weight: 600; font-size: 18px; margin: 24px 0; }
        .solution {
            background: #f7fafc;
            border-left: 4px solid #4299e1;
            padding: 16px;
            margin: 24px 0;
            text-align: left;
        }
        .solution strong { color: #2d3748; display: block; margin-bottom: 8px; }
        code {
            background: #2d3748;
            color: #48bb78;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 14px;
        }
        a {
            display: inline-block;
            background: #4299e1;
            color: white;
            padding: 12px 32px;
            border-radius: 8px;
            text-decoration: none;
            margin-top: 24px;
            font-weight: 600;
            transition: background 0.2s;
        }
        a:hover { background: #3182ce; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 Portfolio Tracker</h1>
        <div class="status">⚠️ Frontend Build Issue</div>
        <p>Le backend API fonctionne correctement, mais le frontend build n'a pas été détecté.</p>
        
        <div class="solution">
            <strong>Diagnostique :</strong>
            <p>Frontend path: <code>{FRONTEND_BUILD or "Not found"}</code></p>
            <br>
            <p>Cela devrait être résolu automatiquement au prochain déploiement.</p>
            <p>Si le problème persiste, contactez le support technique.</p>
        </div>
        
        <p><strong>En attendant, utilisez l'API directement :</strong></p>
        <a href="/docs">📚 Documentation API</a>
    </div>
</body>
</html>
    """, status_code=200)

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Skip API routes
    if full_path.startswith("api/") or full_path in ["docs", "openapi.json", "redoc"]:
        raise HTTPException(status_code=404)
    
    # Serve static files
    if FRONTEND_BUILD:
        file_path = FRONTEND_BUILD / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        # Serve index.html for client-side routing
        index_path = FRONTEND_BUILD / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
    
    raise HTTPException(status_code=404)
