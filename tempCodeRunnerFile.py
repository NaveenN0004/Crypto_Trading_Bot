from config.settings import RISK_REWARD_RATIO, STOP_LOSS_PERCENTAGE # import RISK_REWARD_RATIO, STOP_LOSS_PERCENTAGE from "config/settings.py"
from core.risk_management import calculate_stop_loss, calculate_take_profit # import functions from "core/risk_management.py"
from utils.auth import connect_with_coindcx, fetch_wallet_balances, fetch_market_data  # import authentication functions from "utils/auth.py"

def get_user_input():
    # asking the user for trading pair and investment amount.
    
    print("➡️ Provide Trading Parameters :")
    trading_pair = input("Enter the trading pair (e.g., BTCINR, ETHINR): ").strip().upper()

    while True:
        try:
            investment_amount = float(input("Enter the investment amount in INR: ").strip())
            if investment_amount <= 0:
                raise ValueError("⚠️Investment amount must be greater than zero.")
            break
        except ValueError as e:
            print(f"❌ Invalid input: {e}")

    return trading_pair, investment_amount

def main():

    # function that handles bot execution

    try:
        trading_pair, investment_amount = get_user_input()
        print("\n📝 Trade Summary:")
        print(f"➡️ Trading Pair: {trading_pair}")
        print(f"➡️ Investment Amount: {investment_amount} INR")
    except Exception as e:
        print(f"❌ Error during user input: {str(e)}")

    # authenticate with CoinDCX
    print("\n🔑 Testing API Authentication...")
    try:
        user_info = connect_with_coindcx()
        print(f"🔍 User Info: {user_info}")  # print user info for verification
    except Exception as e:
        print(f"❌ Error during authentication: {str(e)}")
        return  # exit the function if authentication fails

    # fetching wallet balances
    print("\n💰 Fetching Wallet Balances...")
    try:
        fetch_wallet_balances()
    except Exception as e:
        print(f"❌ Error during wallet balance fetch: {str(e)}")
        return  # exit the function if fetching balances fails
    
    # fetch market data for trading pair
    print(f"\n📊 Fetching Market Data...")
    try:
        current_price = fetch_market_data(trading_pair)

        stop_loss_price = calculate_stop_loss(current_price, STOP_LOSS_PERCENTAGE)
        take_profit_price = calculate_take_profit(current_price, STOP_LOSS_PERCENTAGE, RISK_REWARD_RATIO)

        print("\n📉 Risk Management Summary:")
        print(f"➡️ Current Price: {current_price} INR")
        print(f"➡️ Stop-Loss Price: {stop_loss_price} INR")
        print(f"➡️ Take-Profit Price: {take_profit_price} INR")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

if __name__ == "__main__":
    main()