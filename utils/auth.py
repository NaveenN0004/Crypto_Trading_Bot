import hmac
import json
import time
import hashlib
import requests
from config.settings import API_KEY, API_SECRET, DEBUG_MODE, WALLET_THRESHOLD # import API_KEY, API_SECRET, DEBUG_MODE from "config/settings.py"


def connect_with_coindcx():
    # function to authenticate with CoinDCX

    url = "https://api.coindcx.com/exchange/v1/users/info" # endpoint provided by CoinDCX for user information

    # creating payload
    timestamp = int(time.time() * 1000)  # current time in milliseconds
    payload = {"timestamp": timestamp}

    payload_str = str(payload).replace("'", '"')  # ensure valid JSON format
    signature = hmac.new(
        API_SECRET.encode('utf-8'), payload_str.encode('utf-8'), hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": API_KEY,
        "X-AUTH-SIGNATURE": signature,
    }

    if DEBUG_MODE:
        print("🔍 Debugging Info:")
        print(f"➡️ URL: {url}")
        print(f"➡️ Headers: {headers}")
        print(f"➡️ Payload: {payload}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        if DEBUG_MODE:
            print(f"➡️ Response Status Code: {response.status_code}")
            print(f"➡️ Response Text: {response.text}")

        if response.status_code == 200:
            print("✅ Authentication successful!")
            return response.json()  # return response data for further use
        else:
            error_message = f"Authentication failed with status code {response.status_code}"
            if DEBUG_MODE:
                print(f"🔍 Response Content: {response.json()}")
            raise ValueError(error_message)

    except Exception as e:
        if DEBUG_MODE:
            print(f"❌ Error during authentication: {str(e)}")
        raise

def fetch_wallet_balances():
    # function to fetch wallet balances from CoinDCX

    url = "https://api.coindcx.com/exchange/v1/users/balances"
    timestamp = int(time.time() * 1000)
    payload = {"timestamp": timestamp}
    payload_str = str(payload).replace("'", '"')
    signature = hmac.new(
        API_SECRET.encode('utf-8'), payload_str.encode('utf-8'), hashlib.sha256
    ).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": API_KEY,
        "X-AUTH-SIGNATURE": signature,
    }
    if DEBUG_MODE:
        print("🔍 Debugging Info:")
        print(f"➡️ URL: {url}")
        print(f"➡️ Headers: {headers}")
        print(f"➡️ Payload: {payload}")
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            balances = response.json()
            # Extract INR balance
            inr_balance = next(
                (item.get('balance', 0.0) for item in balances if item.get('currency') == 'INR'),
                0.0,
            )
            print(f"💰 Current Wallet Balance (INR): {inr_balance}")
            if inr_balance < WALLET_THRESHOLD:
                print("⚠️ Warning: Wallet balance is below 100 INR. Please add funds!")
            return inr_balance  # Return only the INR balance
        else:
            error_message = f"Failed to fetch wallet balances with status code {response.status_code}"
            if DEBUG_MODE:
                print(f"🔍 Response Content: {response.json()}")
            raise ValueError(error_message)
    except Exception as e:
        if DEBUG_MODE:
            print(f"❌ Error during wallet balance fetch: {str(e)}")
        raise

def fetch_market_data(trading_pair):
    # function to fetch market data for a given trading pair

    url = "https://api.coindcx.com/exchange/ticker"

    try:
        response = requests.get(url)
        if DEBUG_MODE:
            print("🔍 Debugging Info:")
            print(f"➡️ URL: {url}")

        if response.status_code == 200:
            tickers = response.json()
            market_data = next((item for item in tickers if item['market'] == trading_pair), None)

            if market_data:
                current_price = float(market_data.get('last_price', 0.0))
                print(f"📈 Market Data for {trading_pair}:")
                print(f"➡️ Current Price: {current_price} INR")
                print(f"➡️ 24h Change: {market_data.get('change_24_hour', 'N/A')}%")
                print(f"➡️ Lowest Ask: {market_data.get('ask', 'N/A')}")
                print(f"➡️ Highest Bid: {market_data.get('bid', 'N/A')}")

                if DEBUG_MODE:
                    print("🔍 Raw Market Data:")
                    print(json.dumps(market_data, indent=4))
                
                return current_price  # return the price
            else:
                raise ValueError(f"❌ No market data found for trading pair: {trading_pair}")
        else:
            error_message = f"Failed to fetch market data with status code {response.status_code}"
            if DEBUG_MODE:
                print(f"🔍 Response Content: {response.json()}")
            raise ValueError(error_message)

    except Exception as e:
        if DEBUG_MODE:
            print(f"❌ Error during fetching market data: {str(e)}")
        raise