import hmac
import json
import time
import hashlib
import requests
from typing import Any, Dict
from config.settings import API_KEY, API_SECRET, DEBUG_MODE, WALLET_THRESHOLD

class Auth:
    
    # handles API authentication and related requests to CoinDCX
    

    @staticmethod
    def _generate_headers(payload: Dict[str, Any]) -> Dict[str, str]:
        # generate authentication headers using a HMAC SHA256 signature

        payload_str = str(payload).replace("'", '"')
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": API_KEY,
            "X-AUTH-SIGNATURE": signature,
        }

    @staticmethod
    def connect_with_coindcx() -> Dict[str, Any]:        
        # authenticate with CoinDCX and return the user info
        
        url = "https://api.coindcx.com/exchange/v1/users/info"
        timestamp = int(time.time() * 1000)
        payload: Dict[str, Any] = {"timestamp": timestamp}
        headers = Auth._generate_headers(payload)

        if DEBUG_MODE:
            print("🔍 [Auth] Connecting with CoinDCX:")
            print(f"➡️ URL: {url}")
            print(f"➡️ Headers: {headers}")
            print(f"➡️ Payload: {payload}")

        try:
            response = requests.post(url, headers=headers, json=payload)
            if DEBUG_MODE:
                print(f"Response Code: {response.status_code}")
                print(f"Response Text: {response.text}")
            if response.status_code == 200:
                print("✅ Authentication successful!")
                return response.json()
            else:
                if DEBUG_MODE:
                    print(f"Error Response: {response.json()}")
                raise ValueError(f"Authentication failed with status code {response.status_code}")
        except Exception as e:
            if DEBUG_MODE:
                print(f"❌ Authentication error: {e}")
            raise

    @staticmethod
    def fetch_wallet_balances() -> float:        
        # fetch the wallet balances from CoinDCX and return the INR balance
        
        url = "https://api.coindcx.com/exchange/v1/users/balances"
        timestamp = int(time.time() * 1000)
        payload: Dict[str, Any] = {"timestamp": timestamp}
        headers = Auth._generate_headers(payload)

        if DEBUG_MODE:
            print("🔍 [Auth] Fetching wallet balances:")
            print(f"➡️ URL: {url}")
            print(f"➡️ Headers: {headers}")
            print(f"➡️ Payload: {payload}")

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                balances = response.json()
                inr_balance = next(
                    (float(item.get('balance', 0.0)) for item in balances if item.get('currency') == 'INR'),
                    0.0,
                )
                print(f"💰 Wallet Balance (INR): {inr_balance}")
                if inr_balance < WALLET_THRESHOLD:
                    print("⚠️ Warning: Wallet balance is below threshold; please add funds.")
                return inr_balance
            else:
                if DEBUG_MODE:
                    print(f"Error fetching balances: {response.json()}")
                raise ValueError(f"Failed to fetch wallet balances; code: {response.status_code}")
        except Exception as e:
            if DEBUG_MODE:
                print(f"❌ Wallet fetch error: {e}")
            raise

    @staticmethod
    def fetch_market_data(trading_pair: str) -> float:        
        # retrieve real-time market data for the given trading pair and return the current price
        
        url = "https://api.coindcx.com/exchange/ticker"
        if DEBUG_MODE:
            print("🔍 [Auth] Fetching market data...")
        try:
            response = requests.get(url)
            if DEBUG_MODE:
                print(f"Response Code: {response.status_code}")
            if response.status_code == 200:
                tickers = response.json()
                market_data = next((item for item in tickers if item.get('market') == trading_pair), None)
                if market_data:
                    current_price = float(market_data.get('last_price', 0.0))
                    print(f"📈 {trading_pair} Current Price: {current_price} INR")
                    if DEBUG_MODE:
                        print("Raw Market Data:", json.dumps(market_data, indent=2))
                    return current_price
                else:
                    raise ValueError(f"❌ No market data found for {trading_pair}")
            else:
                raise ValueError(f"Failed to fetch market data; code: {response.status_code}")
        except Exception as e:
            if DEBUG_MODE:
                print(f"❌ Market data error: {e}")
            raise
