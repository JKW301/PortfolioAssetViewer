import requests
import sys
import json
from datetime import datetime

class InvestmentTrackerTester:
    def __init__(self, base_url="https://assettracker-27.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_assets = {
            'crypto': [],
            'stocks': [],
            'coins': []
        }

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.text}")
                except:
                    pass
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_portfolio_overview(self):
        """Test portfolio overview endpoint"""
        success, response = self.run_test(
            "Portfolio Overview",
            "GET",
            "portfolio/overview",
            200
        )
        return success, response

    def test_create_crypto(self):
        """Test creating a cryptocurrency"""
        crypto_data = {
            "name": "Bitcoin Test",
            "symbol": "BTC",
            "quantity": 0.1,
            "purchase_price": 45000.0
        }
        success, response = self.run_test(
            "Create Crypto",
            "POST",
            "crypto",
            200,
            data=crypto_data
        )
        if success and 'id' in response:
            self.created_assets['crypto'].append(response['id'])
        return success, response

    def test_get_cryptos(self):
        """Test getting all cryptocurrencies"""
        success, response = self.run_test(
            "Get Cryptos",
            "GET",
            "crypto",
            200
        )
        return success, response

    def test_crypto_price(self, crypto_id):
        """Test getting crypto price"""
        success, response = self.run_test(
            "Get Crypto Price",
            "GET",
            f"crypto/{crypto_id}/price",
            200
        )
        return success, response

    def test_create_stock(self):
        """Test creating a stock"""
        stock_data = {
            "name": "Apple Inc",
            "symbol": "AAPL",
            "quantity": 10,
            "purchase_price": 150.0
        }
        success, response = self.run_test(
            "Create Stock",
            "POST",
            "stocks",
            200,
            data=stock_data
        )
        if success and 'id' in response:
            self.created_assets['stocks'].append(response['id'])
        return success, response

    def test_get_stocks(self):
        """Test getting all stocks"""
        success, response = self.run_test(
            "Get Stocks",
            "GET",
            "stocks",
            200
        )
        return success, response

    def test_stock_price(self, stock_id):
        """Test getting stock price"""
        success, response = self.run_test(
            "Get Stock Price",
            "GET",
            f"stocks/{stock_id}/price",
            200
        )
        return success, response

    def test_create_coin(self):
        """Test creating a coin with scraping"""
        coin_data = {
            "name": "Gold Coin Test",
            "url": "https://example.com",
            "css_selector": ".price",
            "quantity": 5
        }
        success, response = self.run_test(
            "Create Coin",
            "POST",
            "coins",
            200,
            data=coin_data
        )
        if success and 'id' in response:
            self.created_assets['coins'].append(response['id'])
        return success, response

    def test_get_coins(self):
        """Test getting all coins"""
        success, response = self.run_test(
            "Get Coins",
            "GET",
            "coins",
            200
        )
        return success, response

    def test_coin_price(self, coin_id):
        """Test getting coin price (may fail due to scraping)"""
        success, response = self.run_test(
            "Get Coin Price",
            "GET",
            f"coins/{coin_id}/price",
            200
        )
        return success, response

    def test_create_snapshot(self):
        """Test creating a history snapshot"""
        success, response = self.run_test(
            "Create Snapshot",
            "POST",
            "history/snapshot",
            200
        )
        return success, response

    def test_get_snapshots(self):
        """Test getting history snapshots"""
        success, response = self.run_test(
            "Get Snapshots",
            "GET",
            "history/snapshots",
            200
        )
        return success, response

    def test_delete_crypto(self, crypto_id):
        """Test deleting a crypto"""
        success, response = self.run_test(
            "Delete Crypto",
            "DELETE",
            f"crypto/{crypto_id}",
            200
        )
        return success, response

    def test_delete_stock(self, stock_id):
        """Test deleting a stock"""
        success, response = self.run_test(
            "Delete Stock",
            "DELETE",
            f"stocks/{stock_id}",
            200
        )
        return success, response

    def test_delete_coin(self, coin_id):
        """Test deleting a coin"""
        success, response = self.run_test(
            "Delete Coin",
            "DELETE",
            f"coins/{coin_id}",
            200
        )
        return success, response

def main():
    print("🚀 Starting Investment Tracker API Tests")
    print("=" * 50)
    
    tester = InvestmentTrackerTester()
    
    # Test portfolio overview first
    print("\n📊 Testing Portfolio Overview...")
    overview_success, overview_data = tester.test_portfolio_overview()
    
    # Test crypto operations
    print("\n💰 Testing Cryptocurrency Operations...")
    crypto_success, crypto_data = tester.test_create_crypto()
    tester.test_get_cryptos()
    
    if crypto_success and crypto_data.get('id'):
        crypto_id = crypto_data['id']
        print(f"   Testing price for crypto ID: {crypto_id}")
        tester.test_crypto_price(crypto_id)
    
    # Test stock operations
    print("\n📈 Testing Stock Operations...")
    stock_success, stock_data = tester.test_create_stock()
    tester.test_get_stocks()
    
    if stock_success and stock_data.get('id'):
        stock_id = stock_data['id']
        print(f"   Testing price for stock ID: {stock_id}")
        tester.test_stock_price(stock_id)
    
    # Test coin operations
    print("\n🪙 Testing Coin Operations...")
    coin_success, coin_data = tester.test_create_coin()
    tester.test_get_coins()
    
    if coin_success and coin_data.get('id'):
        coin_id = coin_data['id']
        print(f"   Testing price for coin ID: {coin_id}")
        # Note: This may fail due to scraping limitations
        tester.test_coin_price(coin_id)
    
    # Test history operations
    print("\n📊 Testing History Operations...")
    tester.test_create_snapshot()
    tester.test_get_snapshots()
    
    # Test delete operations
    print("\n🗑️ Testing Delete Operations...")
    for crypto_id in tester.created_assets['crypto']:
        tester.test_delete_crypto(crypto_id)
    
    for stock_id in tester.created_assets['stocks']:
        tester.test_delete_stock(stock_id)
    
    for coin_id in tester.created_assets['coins']:
        tester.test_delete_coin(coin_id)
    
    # Final results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Backend API tests mostly successful!")
        return 0
    else:
        print("❌ Backend API tests have significant failures")
        return 1

if __name__ == "__main__":
    sys.exit(main())