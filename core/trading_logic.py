import time
from datetime import datetime, timezone
from typing import Any
from core.OMS import OrderManagementSystem
from config.settings import DEBUG_MODE
from utils.historical_data import HistoricalData
from utils.technical_indicators import TechnicalIndicators
from core.quantity_utils import QuantityUtils
from utils.logging_utils import Logger
from utils.market_data import MarketData
from core.signal_generator import SignalGenerator

class TradingLogic:
    
    # encapsulates the live trading logic: monitoring prices, placing orders, and managing open positions
    
    def __init__(self) -> None:
        self.oms = OrderManagementSystem()
        self.signal_gen = SignalGenerator()
        self.open_positions: dict[str, float] = {}

    def monitor_position(self, trading_pair: str, entry_price: float, quantity: float,
                         stop_loss_price: float, take_profit_price: float,
                         investment_amount: float, wallet_balance: float) -> bool:        
        # monitor an open position and trigger a sell if stop-loss or take-profit is hit
        # returns True for closed position 

        print(f"\n📗 Monitoring position for {trading_pair} (Entry: {entry_price})")
        try:
            while True:
                current_price = MarketData.fetch_real_time_price(trading_pair)
                if current_price is None:
                    print("❌ Failed to fetch current price")
                    time.sleep(5)
                    continue

                unrealized_pnl = (current_price - entry_price) * quantity
                pnl_percentage = (unrealized_pnl / investment_amount) * 100
                current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                print(f"\r🕒 {current_time} UTC | 💹 Current Price: {current_price:.2f} | P&L: {unrealized_pnl:.2f} ({pnl_percentage:.2f}%)", end="")

                if current_price <= stop_loss_price:
                    print(f"\n🛑 Stop Loss triggered at {current_price}")
                    sell_order = self.place_order(
                        order_side="sell",
                        trading_pair=trading_pair,
                        current_price=current_price,
                        investment_amount=investment_amount,
                        wallet_balance=wallet_balance,
                        stop_loss_price=None,
                        take_profit_price=None,
                        initial_price=entry_price
                    )
                    if sell_order:
                        print(f"✅ Stop Loss order executed successfully at {current_time} UTC")
                        Logger.log_trade(
                            trading_pair=trading_pair,
                            current_price=current_price,
                            investment_amount=investment_amount,
                            quantity=quantity,
                            wallet_balance=wallet_balance,
                            order_type="sell",
                            stop_loss_price=None,
                            take_profit_price=None,
                            initial_price=entry_price,
                            profit=(current_price - entry_price) * quantity,
                            sell_price=current_price,
                            buy_price=entry_price
                        )
                    return True

                if current_price >= take_profit_price:
                    print(f"\n🎯 Take Profit triggered at {current_price}")
                    sell_order = self.place_order(
                        order_side="sell",
                        trading_pair=trading_pair,
                        current_price=current_price,
                        investment_amount=investment_amount,
                        wallet_balance=wallet_balance,
                        stop_loss_price=None,
                        take_profit_price=None,
                        initial_price=entry_price
                    )
                    if sell_order:
                        print(f"✅ Take Profit order executed successfully at {current_time} UTC")
                        Logger.log_trade(
                            trading_pair=trading_pair,
                            current_price=current_price,
                            investment_amount=investment_amount,
                            quantity=quantity,
                            wallet_balance=wallet_balance,
                            order_type="sell",
                            stop_loss_price=None,
                            take_profit_price=None,
                            initial_price=entry_price,
                            profit=(current_price - entry_price) * quantity,
                            sell_price=current_price,
                            buy_price=entry_price
                        )
                    return True

                time.sleep(5)
        except Exception as e:
            print(f"\n❌ Error monitoring position: {e}")
            return False

    def place_order(self, order_side: str, trading_pair: str, current_price: float, investment_amount: float,
                    wallet_balance: float, stop_loss_price: Any, take_profit_price: Any,
                    initial_price: Any = None) -> Any:
        # place a buy or sell order using the OMS
        # returns the order object if successful
        
        try:
            market_details = MarketData.get_market_details(trading_pair)
            if not market_details:
                print(f"❌ Failed to fetch market details for {trading_pair}.")
                return None

            quantity = QuantityUtils.calculate_quantity(investment_amount, current_price, market_details)
            if order_side.lower() == "buy":
                order = self.oms.place_market_order(
                    market=trading_pair,
                    side="buy",
                    total_quantity=quantity,
                    stop_loss=stop_loss_price,
                    take_profit=take_profit_price
                )
                initial_price_to_log = current_price
            else:  # sell order
                order = self.oms.place_market_order(
                    market=trading_pair,
                    side="sell",
                    total_quantity=quantity
                )
                initial_price_to_log = initial_price

            # log trade
            if order:
                Logger.log_trade(
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
                    self.open_positions[trading_pair] = current_price
                return order
            print(f"❌ {order_side.capitalize()} Order Failed!")
            return None

        except Exception as e:
            print(f"❌ Error placing {order_side} order: {e}")
            return None

    def monitor_price_and_execute(self, investment_amount: float, trading_pair: str,
                                  stop_loss_price: float, take_profit_price: float) -> None:        
        # continuously monitor market price and execute orders when a signal is detected
        
        print("\n📡 Monitoring Market Price...")
        try:
            while True:
                df = HistoricalData.fetch(trading_pair)
                if df is None:
                    print("❌ Failed to fetch historical data.")
                    time.sleep(5)
                    continue
                df = TechnicalIndicators.calculate(df)
                should_trade, signal = self.signal_gen.analyze_indicators(df)
                current_price = MarketData.fetch_real_time_price(trading_pair)
                if current_price is None:
                    print("❌ Failed to fetch current price.")
                    time.sleep(5)
                    continue
                market_details = MarketData.get_market_details(trading_pair)
                if not market_details:
                    print(f"❌ Failed to fetch market details for {trading_pair}.")
                    time.sleep(5)
                    continue
                print(f"\r🔍 Current Price of {trading_pair}: {current_price:.2f} INR", end="")
                if should_trade:
                    signal_strength = self.signal_gen.get_signal_strength(df)
                    print(f"\n📊 Signal Strength: {signal_strength:.2f}%")
                    if signal.lower() == "buy":
                        print("\n🎯 Buy Signal Detected!")
                        buy_order = self.place_order(
                            "buy", 
                            trading_pair, 
                            current_price, 
                            investment_amount,
                            market_details.get("balance", 0),
                            stop_loss_price,
                            take_profit_price
                        )
                        if buy_order:
                            self.monitor_position(
                                trading_pair=trading_pair,
                                entry_price=current_price,
                                quantity=buy_order.total_quantity,
                                stop_loss_price=stop_loss_price,
                                take_profit_price=take_profit_price,
                                investment_amount=investment_amount,
                                wallet_balance=market_details.get("balance", 0)
                            )
                            break
                    elif signal.lower() == "sell":
                        print("\n🎯 Sell Signal Detected!")
                        entry_price = self.open_positions.get(trading_pair)
                        if entry_price is None:
                            print("⚠️ No recorded entry price for sell order.")
                            continue
                        sell_order = self.place_order(
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
            print(f"\n❌ Error during price monitoring: {e}")
