from config.settings import RISK_REWARD_RATIO, STOP_LOSS_PERCENTAGE
from core.risk_management import RiskManagement
from utils.auth import Auth
from core.trading_logic import TradingLogic
from utils.market_data import MarketData

def get_user_input() -> tuple[str, float]:
    # prompt the user for trading pair and investment amount
    
    print("➡️ Provide Trading Parameters ⬅️")
    trading_pair = input("📈 Enter the trading pair (e.g., BTCINR, ETHINR): ").strip().upper()
    while True:
        try:
            investment_amount = float(input("💰 Enter the investment amount in INR: ").strip())
            RiskManagement.validate_investment_amount(investment_amount)
            break
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
    return trading_pair, investment_amount

def main() -> None:
    # main function
    
    try:
        trading_pair, investment_amount = get_user_input()
        print("\n📝 Trade Summary:")
        print(f"➡️ Trading Pair: {trading_pair}")
        print(f"➡️ Investment Amount: {investment_amount} INR")
    except Exception as e:
        print(f"❌ Error during user input: {e}")
        return

    # connect to CoinDCX
    print("\n🔑 Testing API Authentication...")
    try:
        user_info = Auth.connect_with_coindcx()
        print(f"🔍 User Info: {user_info}")
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return

    # fetch wallet balance
    print("\n💰 Fetching Wallet Balances...")
    try:
        wallet_balance = Auth.fetch_wallet_balances()
    except Exception as e:
        print(f"❌ Error during wallet balance fetch: {e}")
        return

    # fetch market data for Trading Pair
    print(f"\n📊 Fetching Market Data for {trading_pair}...")
    try:
        current_price = MarketData.fetch_real_time_price(trading_pair)
        print(f"📉 Current Price of {trading_pair}: {current_price} INR")
        market_details = MarketData.get_market_details(trading_pair)
        min_investment = market_details["min_quantity"] * current_price
        max_investment = market_details["max_quantity"] * current_price
        if investment_amount < min_investment:
            print(f"❌ Investment amount is too low to meet the minimum quantity of {market_details['min_quantity']}. Minimum required is {min_investment:.2f} INR.")
            return
        if investment_amount > max_investment:
            print(f"❌ Investment amount is too high to meet the maximum quantity of {market_details['max_quantity']}. Maximum allowed is {max_investment:.2f} INR.")
            return
        risk_management = RiskManagement.calculate(current_price, STOP_LOSS_PERCENTAGE, RISK_REWARD_RATIO)
        if risk_management:
            print("\n📉 Risk Management Summary 📈")
            print(f"➡️ Investment Amount: {investment_amount} INR")
            print(f"➡️ Stop-Loss Price: {risk_management['stop_loss_price']} INR")
            print(f"➡️ Take-Profit Price: {risk_management['take_profit_price']} INR")
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # order handling 
    trading_logic = TradingLogic()
    print("\n📥 Placing Buy Order...")
    try:
        buy_order = trading_logic.place_order(
            order_side="buy",
            trading_pair=trading_pair,
            current_price=current_price,
            investment_amount=investment_amount,
            wallet_balance=wallet_balance,
            stop_loss_price=risk_management["stop_loss_price"],
            take_profit_price=risk_management["take_profit_price"]
        )
        if buy_order:
            print("\n✅ Buy order executed successfully!")
            position_closed = trading_logic.monitor_position(
                trading_pair=trading_pair,
                entry_price=current_price,
                quantity=buy_order.total_quantity,
                stop_loss_price=risk_management["stop_loss_price"],
                take_profit_price=risk_management["take_profit_price"],
                investment_amount=investment_amount,
                wallet_balance=wallet_balance
            )
            if not position_closed:
                print("\n⚠️ Position monitoring ended without proper closure")
        else:
            print("❌ Failed to place buy order. Exiting...")
            return
    except Exception as e:
        print(f"❌ Error during buy order: {e}")
        return

if __name__ == "__main__":
    main()
