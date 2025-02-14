import requests
import json
from typing import Any, Dict
from config.settings import DEBUG_MODE

class MarketData:
    
    # provides methods to retrieve market details and real-time price data
    

    @staticmethod
    def get_market_details(trading_pair: str) -> Dict[str, Any]:
        
        # retrieve detailed market information for the specified trading pair
        
        url = "https://api.coindcx.com/exchange/v1/markets_details"
        if DEBUG_MODE:
            print(f"🔍 Fetching market details from URL: {url}")
        try:
            response = requests.get(url)
            if DEBUG_MODE:
                print(f"➡️ Response Status Code: {response.status_code}")
            if response.status_code == 200:
                markets = response.json()
                if DEBUG_MODE:
                    print(f"🔍 Total Markets Fetched: {len(markets)}")
                for market in markets:
                    if market.get('symbol') == trading_pair:
                        if DEBUG_MODE:
                            print(f"🔍 Market details found for {trading_pair}: {market}")
                        return market
                raise ValueError(f"❌ Trading pair {trading_pair} not found.")
            else:
                raise Exception(f"❌ Failed to fetch market details: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Request failed: {e}")

    @staticmethod
    def fetch_real_time_price(trading_pair: str) -> float:   
        # retrieve the current market price for the specified trading pair
        
        url = "https://api.coindcx.com/exchange/ticker"
        if DEBUG_MODE:
            print("🔍 Fetching real-time price from Ticker API.")
        try:
            response = requests.get(url)
            if DEBUG_MODE:
                print(f"➡️ Response Status Code: {response.status_code}")
            if response.status_code == 200:
                ticker_data = response.json()
                if DEBUG_MODE:
                    print(f"🔍 Ticker Data Fetched: {ticker_data}")
                for ticker in ticker_data:
                    if ticker.get("market") == trading_pair:
                        latest_price = float(ticker.get("last_price", 0.0))
                        if DEBUG_MODE:
                            print(f"🔍 Real-Time Price of {trading_pair}: {latest_price}")
                        return latest_price
                raise ValueError(f"❌ Trading pair {trading_pair} not found in Ticker API data.")
            else:
                raise Exception(f"❌ Failed to fetch price: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Request failed: {e}")
