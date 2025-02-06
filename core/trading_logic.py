import time
from datetime import datetime, timezone
from core.OMS import OrderManagementSystem, Order 
from config.settings import DEBUG_MODE
from utils.historical_data import fetch_historical_data
from utils.technical_indicators import calculate_indicators
from core.quantity_utils import calculate_quantity
from utils.logging_utils import log_trade
from utils.market_data import get_market_details, fetch_real_time_price
from core.signal_generator import SignalGenerator


oms = OrderManagementSystem()
open_positions = {}


def monitor_position(
    trading_pair: str,
    entry_price: float,
    quantity: float,
    stop_loss_price: float,
    take_profit_price: float,
    investment_amount: float,
    wallet_balance: float
) -> None:
    # monitors the open position for a given trading pair.
    
    print(f"\n📗 Monitoring position for {trading_pair} (Entry: {entry_price})")
    
    try:
        while True:
            current_price = fetch_real_time_price(trading_pair)
            if current_price is None:
                print("❌ Failed to fetch current price")
                time.sleep(5)
                continue
                
            unrealized_pnl = (current_price - entry_price) * quantity
            pnl_percentage = (unrealized_pnl / investment_amount) * 100
            
            current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\r🕒 {current_time} UTC | 💹 Current Price: {current_price:.2f} | P&L: {unrealized_pnl:.2f} ({pnl_percentage:.2f}%)", end="")
            
            # check for Stop-Loss condition
            if current_price <= stop_loss_price:
                print(f"\n🛑 Stop Loss triggered at {current_price}")
                sell_order = place_order(
                    "sell",
                    trading_pair,
                    current_price,
                    quantity * current_price,
                    wallet_balance,
                    None,
                    None,
                    initial_price=entry_price
                )
                if sell_order:
                    print(f"✅ Stop Loss order executed successfully at {current_time} UTC")
                    log_trade(
                        trading_pair=trading_pair,
                        current_price=current_price,
                        investment_amount=investment_amount,
                        quantity=quantity,
                        wallet_balance=wallet_balance,
                        order_type="sell",
                        stop_loss_price=None,
                        take_profit_price=None,
                        initial_price=entry_price
                    )
                break
                
            # check for Take-Profit condition
            if current_price >= take_profit_price:
                print(f"\n🎯 Take Profit triggered at {current_price}")
                sell_order = place_order(
                    "sell",
                    trading_pair,
                    current_price,
                    quantity * current_price,
                    wallet_balance,
                    None,
                    None,
                    initial_price=entry_price
                )
                if sell_order:
                    print(f"✅ Take Profit order executed successfully at {current_time} UTC")
                    # log the trade
                    log_trade(
                        trading_pair=trading_pair,
                        current_price=current_price,
                        investment_amount=investment_amount,
                        quantity=quantity,
                        wallet_balance=wallet_balance,
                        order_type="sell",
                        stop_loss_price=None,
                        take_profit_price=None,
                        initial_price=entry_price
                    )
                break
                
            time.sleep(5)
            
    except Exception as e:
        print(f"\n❌ Error monitoring position: {str(e)}")


def place_order(order_side, trading_pair, current_price, investment_amount, wallet_balance, stop_loss_price, take_profit_price, initial_price=None):
    # places a buy or sell order using the OMS.
    
    try:
        market_details = get_market_details(trading_pair)
        if not market_details:
            print(f"❌ Failed to fetch market details for {trading_pair}.")
            return None

        quantity = calculate_quantity(investment_amount, current_price, market_details)
        
        if order_side.lower() == "buy":
            order = oms.place_market_order(
                market=trading_pair,
                side="buy",
                total_quantity=quantity,
                stop_loss=stop_loss_price,
                take_profit=take_profit_price
            )
        
            initial_price_to_log = current_price
        else:  # sell order
            order = oms.place_market_order(
                market=trading_pair,
                side="sell",
                total_quantity=quantity
            )
            
            initial_price_to_log = initial_price

        if order:
            # log the trade
            log_trade(
                trading_pair=trading_pair,
                current_price=current_price,
                investment_amount=investment_amount,
                quantity=quantity,
                wallet_balance=wallet_balance,
                order_type=order_side,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                initial_price=initial_price_to_log
            )
            
            print(f"✅ {order_side.capitalize()} Order Successful!")
            if DEBUG_MODE:
                print(f"🔍 Order Details: {order}")

            if order_side.lower() == "buy":
                open_positions[trading_pair] = current_price
            return order

        print(f"❌ {order_side.capitalize()} Order Failed!")
        return None

    except Exception as e:
        print(f"❌ Error placing {order_side} order: {str(e)}")
        return None

def monitor_price_and_execute(investment_amount, trading_pair, stop_loss_price, take_profit_price):
# function that continuously monitors the market price and place triggers buy and sell orders  

    signal_gen = SignalGenerator()
    print("\n📡 Monitoring Market Price...")
    
    try:
        while True:
            df = fetch_historical_data(trading_pair)
            if df is None:
                print("❌ Failed to fetch historical data.")
                time.sleep(5)
                continue
                
            df = calculate_indicators(df)
            should_trade, signal = signal_gen.analyze_indicators(df)
            
            current_price = fetch_real_time_price(trading_pair)
            if current_price is None:
                print("❌ Failed to fetch current price.")
                time.sleep(5)
                continue
            
            market_details = get_market_details(trading_pair)
            if not market_details:
                print(f"❌ Failed to fetch market details for {trading_pair}.")
                time.sleep(5)
                continue
                
            print(f"\r🔍 Current Price of {trading_pair}: {current_price:.2f} INR", end="")
            
            if should_trade:
                signal_strength = signal_gen.get_signal_strength(df)
                print(f"\n📊 Signal Strength: {signal_strength:.2f}%")
                
                if signal.lower() == "buy":
                    print("\n🎯 Buy Signal Detected!")
                    buy_order = place_order(
                        "buy", 
                        trading_pair, 
                        current_price, 
                        investment_amount,
                        market_details.get("balance", 0),
                        stop_loss_price,
                        take_profit_price
                    )
                    
                    if buy_order:
                        monitor_position(
                            trading_pair=trading_pair,
                            entry_price=current_price,
                            quantity=buy_order.get('quantity', 0),
                            stop_loss_price=stop_loss_price,
                            take_profit_price=take_profit_price,
                            investment_amount=investment_amount,
                            wallet_balance=market_details.get("balance", 0)
                        )
                        break
                
                elif signal.lower() == "sell":
                    print("\n🎯 Sell Signal Detected!")

                    entry_price = open_positions.get(trading_pair)
                    if entry_price is None:
                        print("⚠️ No recorded entry price for sell order.")
                        continue
                    sell_order = place_order(
                        "sell",
                        trading_pair,
                        current_price,
                        investment_amount,
                        market_details.get("balance", 0),
                        stop_loss_price,
                        take_profit_price,
                        initial_price=entry_price
                    )
                    if sell_order:
                        break
            
            time.sleep(5)
            
    except Exception as e:
        print(f"\n❌ Error during price monitoring: {str(e)}")
