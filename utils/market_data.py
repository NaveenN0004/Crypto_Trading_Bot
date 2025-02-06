import requests
from config.settings import DEBUG_MODE # import the DEBUG_MODE from "config/settings.py"


def debug_log(message):
    # prints the message if DEBUG_MODE is set to True
    
    if DEBUG_MODE:
        print(f"🔍 Debugging Info: {message}")


def get_market_details(trading_pair):
    # fetches the market details for the given trading pair from CoinDCX.
    
    url = "https://api.coindcx.com/exchange/v1/markets_details" # endpoint to provided by CoinDCX to fetch market details
    debug_log(f"Fetching market details from URL: {url}")
    
    try:
        response = requests.get(url)
        debug_log(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            markets = response.json()
            debug_log(f"Total Markets Fetched: {len(markets)}")
            
            for market in markets:
                if market['symbol'] == trading_pair:
                    debug_log(f"Market details found for {trading_pair}: {market}")
                    return market
            
            raise ValueError(f"❌ Trading pair {trading_pair} not found.")
        else:
            raise Exception(f"❌ Failed to fetch market details: {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Request failed: {e}")

def fetch_real_time_price(trading_pair):
    # fetches the real-time price for the given trading pair from CoinDCX.
    
    url = "https://api.coindcx.com/exchange/ticker" # endpoint to provided by CoinDCX to fetch real-time price

    #debugging info
    debug_log(f"Fetching real-time price from Ticker API.")

    try:
        response = requests.get(url)
        debug_log(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            ticker_data = response.json()
            debug_log(f"Ticker Data Fetched: {ticker_data}")
            # find the trading pair in the ticker data
            for ticker in ticker_data:
                if ticker["market"] == trading_pair:
                    latest_price = float(ticker["last_price"])
                    debug_log(f"Real-Time Price of {trading_pair}: {latest_price}")
                    return latest_price

            raise ValueError(f"❌ Trading pair {trading_pair} not found in Ticker API data.")
        else:
            raise Exception(f"❌ Failed to fetch price: {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Request failed: {e}")