import os
import requests
import pandas as pd
from typing import Optional
from config.settings import GRANULARITY, DEBUG_MODE
from utils.market_data import MarketData

class HistoricalData:
    
    # retrieves historical OHLCV (open, high, low, close, volume) data for a given trading pair
    
    @staticmethod
    def fetch(trading_pair: str, timeframe: str = GRANULARITY, limit: int = 100) -> Optional[pd.DataFrame]:        
        # fetch historical candle data and return a DataFrame
        
        market_details = MarketData.get_market_details(trading_pair)
        if not market_details:
            print(f"❌ Failed to fetch market details for {trading_pair}.")
            return None
        api_pair = market_details.get("pair")
        if not api_pair:
            print(f"❌ No API pair found for trading pair: {trading_pair}.")
            return None

        url = f"https://public.coindcx.com/market_data/candles?pair={api_pair}&interval={timeframe}"
        if DEBUG_MODE:
            print("🔍 Debugging Info:")
            print(f"➡️ URL: {url}")
            print(f"➡️ Trading Pair: {trading_pair}")
            print(f"➡️ Timeframe: {timeframe}")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if DEBUG_MODE:
                    print("🔍 Raw API Response:")
                    print(data)
                df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume"])
                if DEBUG_MODE:
                    print("🔍 DataFrame Before Timestamp Conversion:")
                    print(df.head())
                df["timestamp"] = pd.to_datetime(df["time"], unit="ms", errors="coerce")
                df.set_index("timestamp", inplace=True)
                df.drop(columns=["time"], inplace=True)
                if DEBUG_MODE:
                    print("🔍 DataFrame After Timestamp Conversion:")
                    print(df.head())
                    print("✅ Historical Data Fetched Successfully!")
                    print("🔍 Last 5 Rows of Historical Data:")
                    print(df.tail())
                return df
            else:
                if DEBUG_MODE:
                    print(f"❌ Failed to fetch historical data: {response.status_code}")
                    print(f"🔍 Response Content: {response.json()}")
                raise Exception(f"Failed to fetch historical data: {response.status_code}")
        except Exception as e:
            print(f"❌ Error fetching historical data: {e}")
            return None
