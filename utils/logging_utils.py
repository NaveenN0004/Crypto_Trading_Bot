import os
import pandas as pd
from datetime import datetime
from typing import Any, Dict

class Logger:
    
    # logger class to record trade details to a CSV file
    
    LOGS_FOLDER = "logs"
    LOG_FILE = "trades.csv"

    @staticmethod
    def _get_log_file_path() -> str:
        os.makedirs(Logger.LOGS_FOLDER, exist_ok=True)
        return os.path.join(Logger.LOGS_FOLDER, Logger.LOG_FILE)

    @staticmethod
    def log_trade(trading_pair: str, current_price: float, investment_amount: float,
                  quantity: float, wallet_balance: float, order_type: str,
                  stop_loss_price: Any, take_profit_price: Any,
                  initial_price: Any = None, profit: Any = None,
                  buy_price: Any = None, sell_price: Any = None) -> None:
        
        # log trade details
        # parameters:
        #  - trading_pair: Trading pair (e.g., BTCINR)
        #  - current_price: Price at time of trade logging
        #  - investment_amount: Investment amount in INR
        #  - quantity: Quantity traded
        #  - wallet_balance: Wallet balance after trade
        #  - order_type: "buy" or "sell"
        #  - stop_loss_price, take_profit_price: Risk management levels
        #  - initial_price: Price at which position was opened (for sell orders)
        #  - profit: Realized profit (if applicable)
        #  - buy_price: The price at which asset was bought
        #  - sell_price: The price at which asset was sold
        
        log_entry: Dict[str, Any] = {
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Trading Pair": trading_pair,
            "Order Type": order_type.capitalize(),
            "Current Price": current_price,
            "Investment": investment_amount,
            "Quantity": quantity,
            "Wallet Balance": wallet_balance,
            "Stop-Loss Price": stop_loss_price,
            "Take-Profit Price": take_profit_price,
            "Initial Price": initial_price,
            "Buy Price": buy_price,
            "Sell Price": sell_price,
            "Profit": profit
        }
        df = pd.DataFrame([log_entry])
        log_file_path = Logger._get_log_file_path()
        df.to_csv(log_file_path, mode='a' if os.path.exists(log_file_path) else 'w',
                  header=not os.path.exists(log_file_path), index=False)
        print(f"✅ {order_type.capitalize()} trade logged successfully!")
