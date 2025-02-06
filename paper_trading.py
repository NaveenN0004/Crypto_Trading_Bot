import time
import math
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List
from config.settings import DEBUG_MODE

# import live data and utility functions
from utils.market_data import fetch_real_time_price, get_market_details
from utils.historical_data import fetch_historical_data
from utils.technical_indicators import calculate_indicators
from core.signal_generator import SignalGenerator
from core.quantity_utils import calculate_quantity
from core.risk_management import calculate_risk_management, validate_investment_amount
from utils.logging_utils import log_trade

# -------------------------------
# Paper Trading Order Dataclass
# -------------------------------

@dataclass
class PaperOrder:
    order_id: str
    market: str
    side: str         # "buy" or "sell"
    order_type: str   # "market_order"
    price_per_unit: float
    total_quantity: float
    timestamp: int
    status: str       # e.g., "FILLED"
    fee: float = 0.0
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    avg_price: float = 0.0

# -------------------------------
# Paper Trading OMS Simulation with Trailing Stop-Loss
# -------------------------------

class PaperTradingOMS:
    def __init__(self, initial_balance: float):
        self.wallet_balance = initial_balance
        self.order_history: List[PaperOrder] = []
        self.order_counter = 0

    def _generate_order_id(self) -> str:
        self.order_counter += 1
        return f"PAPER_ORDER_{self.order_counter}"

    def place_market_order(self, market: str, side: str, total_quantity: float,
                           stop_loss: Optional[float] = None, take_profit: Optional[float] = None,
                           execution_price: Optional[float] = None) -> Optional[PaperOrder]:
        
        # simulates placing a market order using the provided execution_price.
        
        if execution_price is None:
            print("❌ [Paper Trading] Execution price must be provided.")
            return None

        slippage_factor = 1.0  # No slippage by default
        simulated_price = execution_price * slippage_factor
        cost = total_quantity * simulated_price

        if side.lower() == "buy":
            if cost > self.wallet_balance:
                print("❌ [Paper Trading] Insufficient funds in virtual wallet.")
                return None
            self.wallet_balance -= cost
        elif side.lower() == "sell":
            self.wallet_balance += cost

        order = PaperOrder(
            order_id=self._generate_order_id(),
            market=market,
            side=side,
            order_type="market_order",
            price_per_unit=simulated_price,
            total_quantity=total_quantity,
            timestamp=int(time.time() * 1000),
            status="FILLED",
            filled_quantity=total_quantity,
            remaining_quantity=0,
            avg_price=simulated_price
        )
        self.order_history.append(order)

        if DEBUG_MODE:
            print(f"🔍 [Paper Trading] Order placed: {order}")
            print(f"🔍 [Paper Trading] Virtual Wallet Balance: {self.wallet_balance:.2f}")

        # log the trade
        log_trade(
            trading_pair=market,
            current_price=simulated_price,
            investment_amount=cost,
            quantity=total_quantity,
            wallet_balance=self.wallet_balance,
            order_type=side,
            stop_loss_price=stop_loss,
            take_profit_price=take_profit,
            initial_price=(simulated_price if side.lower() == "buy" else None)
        )
        return order

# -------------------------------
# Paper Trading Environment Logic with Trailing Stop-Loss
# -------------------------------

open_positions = {}  # e.g., { "ADAINR": entry_price }

def paper_trade_main():
    
    # main function for the paper trading environment.
    # prompts for trading pair and investment amount, places a buy order, then monitors the position.
    
    trading_pair = input("Enter the trading pair for paper trading (e.g., ADAINR): ").strip().upper()
    try:
        investment_amount = float(input("Enter the investment amount in INR for paper trading: ").strip())
        validate_investment_amount(investment_amount)
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        return

    paper_oms = PaperTradingOMS(initial_balance=investment_amount)
    
    current_price = fetch_real_time_price(trading_pair)
    if current_price is None:
        print("❌ Failed to fetch live price.")
        return

    market_details = get_market_details(trading_pair)
    if not market_details:
        print("❌ Failed to fetch market details.")
        return

    risk_mgmt = calculate_risk_management(current_price, 0.01, 1.5)  # 1% stop-loss, risk-reward ratio 1.5

    print(f"\n📊 Live Data for {trading_pair}:")
    print(f"➡️ Current Price: {current_price:.2f} INR")
    print(f"➡️ Risk Management: Initial Stop-Loss = {risk_mgmt['stop_loss_price']} INR, Take-Profit = {risk_mgmt['take_profit_price']} INR")

    quantity = calculate_quantity(investment_amount, current_price, market_details)
    print(f"📈 Calculated Quantity: {quantity}")

    # place a simulated buy order and store the entry price
    buy_order = paper_oms.place_market_order(
        market=trading_pair,
        side="buy",
        total_quantity=quantity,
        stop_loss=risk_mgmt['stop_loss_price'],
        take_profit=risk_mgmt['take_profit_price'],
        execution_price=current_price
    )

    if not buy_order:
        print("❌ Paper trading buy order failed.")
        return

    print("✅ Paper trading buy order executed successfully.")
    open_positions[trading_pair] = current_price  

    simulate_monitor_position(
        trading_pair, 
        current_price, 
        quantity,
        initial_stop_loss=risk_mgmt['stop_loss_price'],
        take_profit_price=risk_mgmt['take_profit_price'],
        paper_oms=paper_oms,
        investment_amount=investment_amount,
        trailing_stop_percentage=0.005,
        polling_interval=5
    )

def simulate_monitor_position(trading_pair: str, entry_price: float, quantity: float,
                              initial_stop_loss: float, take_profit_price: float,
                              paper_oms: PaperTradingOMS, investment_amount: float,
                              trailing_stop_percentage: float = 0.005,
                              polling_interval: int = 5):
    
    # monitors live prices and triggers a sell order if the trailing stop-loss or take-profit condition is met.
    # the trailing stop-loss starts at the initial stop-loss value and is updated as the price rises.
    
    trailing_stop = initial_stop_loss
    max_price = entry_price

    print(f"\n📗 [Paper Trading] Monitoring position for {trading_pair} with Trailing Stop-Loss (simulated)...")
    while True:
        live_price = fetch_real_time_price(trading_pair)
        if live_price is None:
            print("❌ [Paper Trading] Failed to fetch live price, retrying...")
            time.sleep(polling_interval)
            continue

        # update maximum price and adjust trailing stop-loss if price increases
        if live_price > max_price:
            max_price = live_price
            new_trailing = max_price * (1 - trailing_stop_percentage)
            if new_trailing > trailing_stop:
                trailing_stop = new_trailing

        unrealized_pnl = (live_price - entry_price) * quantity
        pnl_percentage = (unrealized_pnl / (entry_price * quantity)) * 100

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\r🕒 {current_time} | Price: {live_price:.2f} INR | P&L: {unrealized_pnl:.2f} ({pnl_percentage:.2f}%) | Trailing Stop: {trailing_stop:.2f} INR", end="")

        # if live price falls to or below the trailing stop, trigger a sell order.
        if live_price <= trailing_stop:
            print(f"\n🛑 [Paper Trading] Trailing Stop-Loss triggered at {live_price:.2f} INR")
            entry_price_for_sell = open_positions.get(trading_pair, entry_price)
            paper_oms.place_market_order(
                market=trading_pair,
                side="sell",
                total_quantity=quantity,
                execution_price=live_price
            )
            log_trade(
                trading_pair=trading_pair,
                current_price=live_price,
                investment_amount=investment_amount,
                quantity=quantity,
                wallet_balance=paper_oms.wallet_balance,
                order_type="sell",
                stop_loss_price=None,
                take_profit_price=None,
                initial_price=entry_price_for_sell
            )
            break
        
        elif live_price >= take_profit_price:
            print(f"\n🎯 [Paper Trading] Take Profit triggered at {live_price:.2f} INR")
            entry_price_for_sell = open_positions.get(trading_pair, entry_price)
            paper_oms.place_market_order(
                market=trading_pair,
                side="sell",
                total_quantity=quantity,
                execution_price=live_price
            )
            log_trade(
                trading_pair=trading_pair,
                current_price=live_price,
                investment_amount=investment_amount,
                quantity=quantity,
                wallet_balance=paper_oms.wallet_balance,
                order_type="sell",
                stop_loss_price=None,
                take_profit_price=None,
                initial_price=entry_price_for_sell
            )
            break

        time.sleep(polling_interval)

if __name__ == "__main__":
    paper_trade_main()