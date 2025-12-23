from fastapi import FastAPI, APIRouter, HTTPException, Request, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from binance.client import Client
from auth import exchange_session_id, get_current_user, logout_user, User

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Binance client (lazy initialization)
binance_api_key = os.environ.get('BINANCE_API_KEY', '')
binance_client = None

def get_binance_client():
    global binance_client
    if binance_client is None:
        try:
            binance_client = Client(binance_api_key, '', testnet=False)
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            binance_client = False
    return binance_client if binance_client is not False else None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class SessionIdRequest(BaseModel):
    session_id: str

class CryptoAsset(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    symbol: str
    quantity: float
    purchase_price: float
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CryptoAssetCreate(BaseModel):
    name: str
    symbol: str
    quantity: float
    purchase_price: float

class StockAsset(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    symbol: str
    quantity: float
    purchase_price: float
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StockAssetCreate(BaseModel):
    name: str
    symbol: str
    quantity: float
    purchase_price: float

class CoinAsset(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    css_selector: str
    quantity: float
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CoinAssetCreate(BaseModel):
    name: str
    url: str
    css_selector: str
    quantity: float

class HistorySnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_value_eur: float
    crypto_value_eur: float
    stocks_value_eur: float
    coins_value_eur: float
    user_id: str

# Helper functions for dependency injection
async def get_db_dependency(request: Request):
    return db

# Auth routes
@api_router.post("/auth/session")
async def create_session(req: SessionIdRequest, response: Response):
    """Exchange session_id for session_token and user data"""
    result = await exchange_session_id(req.session_id, db)
    
    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=result['session_token'],
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,  # 7 days
        path="/"
    )
    
    return result

@api_router.get("/auth/me", response_model=User)
async def get_me(request: Request):
    """Get current user from session"""
    return await get_current_user(request, db)

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    session_token = request.cookies.get('session_token')
    if session_token:
        await logout_user(session_token, db)
    
    response.delete_cookie("session_token", path="/")
    return {"message": "Logged out successfully"}

# Helper functions
def get_eur_usd_rate():
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        data = response.json()
        return data['rates']['EUR']
    except:
        return 0.92

async def get_crypto_price_eur(symbol: str) -> Optional[float]:
    try:
        client = get_binance_client()
        if client is None:
            return None
        ticker = client.get_symbol_ticker(symbol=f"{symbol.upper()}USDT")
        usd_price = float(ticker['price'])
        eur_rate = get_eur_usd_rate()
        return usd_price * eur_rate
    except Exception as e:
        logger.error(f"Error fetching crypto price for {symbol}: {e}")
        return None

async def get_stock_price_eur(symbol: str) -> Optional[float]:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d')
        if not hist.empty:
            usd_price = hist['Close'].iloc[-1]
            eur_rate = get_eur_usd_rate()
            return usd_price * eur_rate
        return None
    except:
        return None

async def get_coin_price_eur(url: str, css_selector: str) -> Optional[float]:
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        element = soup.select_one(css_selector)
        if element:
            price_text = element.get_text().strip()
            price_text = price_text.replace('€', '').replace(',', '.').replace(' ', '')
            import re
            match = re.search(r'(\d+\.?\d*)', price_text)
            if match:
                return float(match.group(1))
        return None
    except:
        return None

# Crypto endpoints
@api_router.post("/crypto", response_model=CryptoAsset)
async def create_crypto(asset: CryptoAssetCreate, request: Request):
    current_user = await get_current_user(request, db)
    asset_data = asset.model_dump()
    asset_data['user_id'] = current_user.user_id
    asset_obj = CryptoAsset(**asset_data)
    doc = asset_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.crypto_assets.insert_one(doc)
    return asset_obj

@api_router.get("/crypto", response_model=List[CryptoAsset])
async def get_cryptos(request: Request):
    current_user = await get_current_user(request, db)
    cryptos = await db.crypto_assets.find({"user_id": current_user.user_id}, {"_id": 0}).to_list(1000)
    for crypto in cryptos:
        if isinstance(crypto['created_at'], str):
            crypto['created_at'] = datetime.fromisoformat(crypto['created_at'])
    return cryptos

@api_router.delete("/crypto/{crypto_id}")
async def delete_crypto(crypto_id: str, request: Request):
    current_user = await get_current_user(request, db)
    result = await db.crypto_assets.delete_one({"id": crypto_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Crypto not found")
    return {"message": "Deleted successfully"}

@api_router.get("/crypto/{crypto_id}/price")
async def get_crypto_current_price(crypto_id: str, request: Request):
    current_user = await get_current_user(request, db)
    crypto = await db.crypto_assets.find_one({"id": crypto_id, "user_id": current_user.user_id}, {"_id": 0})
    if not crypto:
        raise HTTPException(status_code=404, detail="Crypto not found")
    
    price_eur = await get_crypto_price_eur(crypto['symbol'])
    if price_eur is None:
        raise HTTPException(status_code=500, detail="Unable to fetch price")
    
    return {
        "symbol": crypto['symbol'],
        "current_price_eur": price_eur,
        "total_value_eur": price_eur * crypto['quantity']
    }

# Stock endpoints
@api_router.post("/stocks", response_model=StockAsset)
async def create_stock(asset: StockAssetCreate, request: Request):
    asset_obj = StockAsset(**asset.model_dump())
    doc = asset_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.stock_assets.insert_one(doc)
    return asset_obj

@api_router.get("/stocks", response_model=List[StockAsset])
async def get_stocks(request: Request):
    stocks = await db.stock_assets.find({}, {"_id": 0}).to_list(1000)
    for stock in stocks:
        if isinstance(stock['created_at'], str):
            stock['created_at'] = datetime.fromisoformat(stock['created_at'])
    return stocks

@api_router.delete("/stocks/{stock_id}")
async def delete_stock(stock_id: str, request: Request):
    result = await db.stock_assets.delete_one({"id": stock_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"message": "Deleted successfully"}

@api_router.get("/stocks/{stock_id}/price")
async def get_stock_current_price(stock_id: str, request: Request):
    stock = await db.stock_assets.find_one({"id": stock_id}, {"_id": 0})
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    price_eur = await get_stock_price_eur(stock['symbol'])
    if price_eur is None:
        raise HTTPException(status_code=500, detail="Unable to fetch price")
    
    return {
        "symbol": stock['symbol'],
        "current_price_eur": price_eur,
        "total_value_eur": price_eur * stock['quantity']
    }

# Coin endpoints
@api_router.post("/coins", response_model=CoinAsset)
async def create_coin(asset: CoinAssetCreate, request: Request):
    asset_obj = CoinAsset(**asset.model_dump())
    doc = asset_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.coin_assets.insert_one(doc)
    return asset_obj

@api_router.get("/coins", response_model=List[CoinAsset])
async def get_coins(request: Request):
    coins = await db.coin_assets.find({}, {"_id": 0}).to_list(1000)
    for coin in coins:
        if isinstance(coin['created_at'], str):
            coin['created_at'] = datetime.fromisoformat(coin['created_at'])
    return coins

@api_router.delete("/coins/{coin_id}")
async def delete_coin(coin_id: str, request: Request):
    result = await db.coin_assets.delete_one({"id": coin_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Coin not found")
    return {"message": "Deleted successfully"}

@api_router.get("/coins/{coin_id}/price")
async def get_coin_current_price(coin_id: str, request: Request):
    coin = await db.coin_assets.find_one({"id": coin_id}, {"_id": 0})
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    price_eur = await get_coin_price_eur(coin['url'], coin['css_selector'])
    if price_eur is None:
        raise HTTPException(status_code=500, detail="Unable to fetch price")
    
    return {
        "name": coin['name'],
        "current_price_eur": price_eur,
        "total_value_eur": price_eur * coin['quantity']
    }

# Portfolio overview
@api_router.get("/portfolio/overview")
async def get_portfolio_overview(request: Request):
    cryptos = await db.crypto_assets.find({}, {"_id": 0}).to_list(1000)
    stocks = await db.stock_assets.find({}, {"_id": 0}).to_list(1000)
    coins = await db.coin_assets.find({}, {"_id": 0}).to_list(1000)
    
    crypto_value = 0
    for crypto in cryptos:
        price = await get_crypto_price_eur(crypto['symbol'])
        if price:
            crypto_value += price * crypto['quantity']
    
    stocks_value = 0
    for stock in stocks:
        price = await get_stock_price_eur(stock['symbol'])
        if price:
            stocks_value += price * stock['quantity']
    
    coins_value = 0
    for coin in coins:
        price = await get_coin_price_eur(coin['url'], coin['css_selector'])
        if price:
            coins_value += price * coin['quantity']
    
    total_value = crypto_value + stocks_value + coins_value
    
    return {
        "total_value_eur": round(total_value, 2),
        "crypto_value_eur": round(crypto_value, 2),
        "stocks_value_eur": round(stocks_value, 2),
        "coins_value_eur": round(coins_value, 2),
        "crypto_count": len(cryptos),
        "stocks_count": len(stocks),
        "coins_count": len(coins)
    }

# History endpoints
@api_router.post("/history/snapshot")
async def create_snapshot(request: Request):
    overview = await get_portfolio_overview()
    snapshot = HistorySnapshot(
        total_value_eur=overview['total_value_eur'],
        crypto_value_eur=overview['crypto_value_eur'],
        stocks_value_eur=overview['stocks_value_eur'],
        coins_value_eur=overview['coins_value_eur']
    )
    doc = snapshot.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.history_snapshots.insert_one(doc)
    return snapshot

@api_router.get("/history/snapshots", response_model=List[HistorySnapshot])
async def get_snapshots(request: Request):
    snapshots = await db.history_snapshots.find({}, {"_id": 0}).sort('timestamp', -1).to_list(1000)
    for snapshot in snapshots:
        if isinstance(snapshot['timestamp'], str):
            snapshot['timestamp'] = datetime.fromisoformat(snapshot['timestamp'])
    return snapshots

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()