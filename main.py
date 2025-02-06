from config.settings import RISK_REWARD_RATIO, STOP_LOSS_PERCENTAGE  # configurations
from core.risk_management import calculate_risk_management, validate_investment_amount  # risk management functions
from utils.auth import connect_with_coindcx, fetch_wallet_balances, fetch_market_data  # authentication and market data
from core.trading_logic import monitor_position, place_order, monitor_price_and_execute  # trading logic
from utils.market_data import get_market_details  # market details


def get_user_input():
    # get trading pair and investment amount from user input

    print("➡️ Provide Trading Parameters ⬅️")
    trading_pair = input("📈 Enter the trading pair (e.g., BTCINR, ETHINR): ").strip().upper()

    while True:
        try:
            investment_amount = float(input("💰 Enter the investment amount in INR: ").strip())
            validate_investment_amount(investment_amount) # validate investment amount
            break
        except ValueError as e:
            print(f"❌ Invalid input: {e}")

    return trading_pair, investment_amount


def main():
    # main function to execute the trading bot
    
    try:
        # get user input
        trading_pair, investment_amount = get_user_input()
        print("\n📝 Trade Summary:")
        print(f"➡️ Trading Pair: {trading_pair}")
        print(f"➡️ Investment Amount: {investment_amount} INR")
    except Exception as e:
        print(f"❌ Error during user input: {str(e)}")
        return

    # authenticate with CoinDCX
    print("\n🔑 Testing API Authentication...")
    try:
        user_info = connect_with_coindcx()
        print(f"🔍 User Info: {user_info}")
    except Exception as e:
        print(f"❌ Error during authentication: {str(e)}")
        return

    # fetch wallet balances
    print("\n💰 Fetching Wallet Balances...")
    try:
        wallet_balance = fetch_wallet_balances()
    except Exception as e:
        print(f"❌ Error during wallet balance fetch: {str(e)}")
        return

    # fetch market data for the trading pair
    print(f"\n📊 Fetching Market Data for {trading_pair}...")
    try:
        current_price = fetch_market_data(trading_pair)
        print(f"📉 Current Price of {trading_pair}: {current_price} INR")

        # fetch market details
        market_details = get_market_details(trading_pair)
        min_investment = market_details["min_quantity"] * current_price
        max_investment = market_details["max_quantity"] * current_price

        # validate investment amount
        if investment_amount < min_investment:
            print(
                f"❌ Investment amount is too low to meet the minimum quantity of {market_details['min_quantity']}. "
                f"Minimum required is {min_investment:.2f} INR."
            )
            return
        if investment_amount > max_investment:
            print(
                f"❌ Investment amount is too high to meet the maximum quantity of {market_details['max_quantity']}. "
                f"Maximum allowed is {max_investment:.2f} INR."
            )
            return

        # calculate risk management levels
        risk_management = calculate_risk_management(
            current_price, STOP_LOSS_PERCENTAGE, RISK_REWARD_RATIO
        )
        if risk_management:
            print("\n📉 Risk Management Summary 📈")
            print(f"➡️ Investment Amount: {investment_amount} INR")
            print(f"➡️ Stop-Loss Price: {risk_management['stop_loss_price']} INR")
            print(f"➡️ Take-Profit Price: {risk_management['take_profit_price']} INR")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

    # place buy order
    print("\n📥 Placing Buy Order...")
    try:
        buy_order = place_order(
            order_side="buy",
            trading_pair=trading_pair,
            current_price=current_price,
            investment_amount=investment_amount,
            wallet_balance=wallet_balance,
            stop_loss_price=risk_management["stop_loss_price"],
            take_profit_price=risk_management["take_profit_price"],
        )
        
        if buy_order:
            print("\n✅ Buy order executed successfully!")
            # monitor the position after successful buy
            
            position_closed = monitor_position(
                trading_pair=trading_pair,
                entry_price=current_price,
                quantity=buy_order.get('quantity', 0),
                stop_loss_price=risk_management["stop_loss_price"],
                take_profit_price=risk_management["take_profit_price"],
                investment_amount=investment_amount,
                wallet_balance=wallet_balance
            )
            
            if not position_closed:
                print("\n⚠️ Position monitoring ended without proper closure")
                # Optionally implement fallback logic here
        else:
            print("❌ Failed to place buy order. Exiting...")
            return
            
    except Exception as e:
        print(f"❌ Error during buy order: {str(e)}")
        return


# this function is no longer made to use directly as the OMS has been created 
# **(uncomment and use if you dont want your bot to scale with the OMS)** 
"""
    # monitor price and execute sell
    print("\n📈 Monitoring Price for Sell...")
    try:
        monitor_price_and_execute(
            investment_amount,
            trading_pair,
            risk_management["stop_loss_price"],
            risk_management["take_profit_price"],
        )
    except Exception as e:
        print(f"❌ Error during price monitoring: {str(e)}")
        return
"""

if __name__ == "__main__":
    main()