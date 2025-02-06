import os
import requests
import pandas as pd
from utils.market_data import get_market_details # import get_market_details function from "utils/market_data.py"
from config.settings import GRANULARITY, DEBUG_MODE # import the HISTORICAL_DATA_TIMEFRAME and DEBUG_MODE from "config/settings.py"

def fetch_historical_data(trading_pair, timeframe = GRANULARITY, limit=100):
    # fetches historical price data for the trading pair

    market_details = get_market_details(trading_pair)
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

            # Convert the data to a DataFrame
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
            error_message = f"Failed to fetch historical data: {response.status_code}"
            if DEBUG_MODE:
                print(f"🔍 Response Content: {response.json()}")
            raise Exception(error_message)
    except Exception as e:
        print(f"❌ Error fetching historical data: {str(e)}")
        return None