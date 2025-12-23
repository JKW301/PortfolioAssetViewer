from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from binance.client import Client

from database import (
    get_db, init_db,
    CryptoAsset as DBCryptoAsset,
    StockAsset as DBStockAsset,
    CoinAsset as DBCoinAsset,
    HistorySnapshot as DBHistorySnapshot
)
from auth_pg import exchange_session_id, get_current_user, logout_user, User

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Frontend build directory
FRONTEND_BUILD = ROOT_DIR.parent / "frontend" / "build"

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
    id: str
    name: str
    symbol: str
    quantity: float
    purchase_price: float
    created_at: datetime
    class Config:
        from_attributes = True

class StockAssetCreate(BaseModel):
    name: str
    symbol: str
    quantity: float
    purchase_price: float

class StockAssetResponse(BaseModel):
    id: str
    name: str
    symbol: str
    quantity: float
    purchase_price: float
    created_at: datetime
    class Config:
        from_attributes = True

class CoinAssetCreate(BaseModel):
    name: str
    url: str
    css_selector: str
    quantity: float

class CoinAssetResponse(BaseModel):
    id: str
    name: str
    url: str
    css_selector: str
    quantity: float
    created_at: datetime
    class Config:
        from_attributes = True

class HistorySnapshotResponse(BaseModel):
    id: str
    timestamp: datetime
    total_value_eur: float
    crypto_value_eur: float
    stocks_value_eur: float
    coins_value_eur: float
    class Config:
        from_attributes = True

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
@api_router.post("/auth/session")
async def create_session(req: SessionIdRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await exchange_session_id(req.session_id, db)
    response.set_cookie(key="session_token", value=result['session_token'], httponly=True, secure=True, samesite="none", max_age=7*24*60*60, path="/")
    return result

@api_router.get("/auth/me", response_model=User)
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    return await get_current_user(request, db)

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    session_token = request.cookies.get('session_token')
    if session_token:
        await logout_user(session_token, db)
    response.delete_cookie("session_token", path="/")
    return {"message": "Logged out successfully"}

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
    allow_origins=os.environ.get('CORS_ORIGINS', 'https://patrimoine-090973d2f6ba.herokuapp.com,*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from frontend build
if FRONTEND_BUILD.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD / "static")), name="static")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve frontend React app"""
    index_path = FRONTEND_BUILD / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("""
    <html>
        <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #09090B; color: white;">
            <h1>Portfolio Tracker</h1>
            <p>Backend Running ✅</p>
            <p><a href="/docs" style="color: #10B981;">API Documentation</a></p>
        </body>
    </html>
    """)

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_frontend(full_path: str):
    """Catch-all route for React Router"""
    # Check if it's an API route
    if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json":
        raise HTTPException(status_code=404)
    
    # Serve static files
    file_path = FRONTEND_BUILD / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Otherwise serve index.html for React Router
    index_path = FRONTEND_BUILD / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404)

@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("Database tables created successfully")
