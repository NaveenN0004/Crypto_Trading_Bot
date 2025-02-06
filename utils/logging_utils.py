import os
import pandas as pd
from datetime import datetime

def log_trade(trading_pair, current_price, investment_amount, quantity, wallet_balance, order_type, stop_loss_price, take_profit_price, initial_price=None):
    # logs trade details to an CSV file in the 'logs' folder

    # creating logs folder 
    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    # file path
    log_file_path = os.path.join(logs_folder, "trades.csv")

    # initial P&L = 0.0
    profit_loss = 0.0
    profit_loss_percent = 0.0
    
    # log entry
    log_entry = {
        "Time": [datetime.now().strftime("%H:%M:%S")],
        "Trading Pair": [trading_pair],
        "Current Price": [current_price],
        "Investment": [investment_amount],
        "Quantity": [quantity],
        "Wallet Balance": [wallet_balance],
        "Order Type": [order_type.capitalize()],
        "Stop-Loss Price": [stop_loss_price],
        "Take-Profit Price": [take_profit_price],
        "Initial Price": [initial_price]
    }

    # convert log entry to DataFrame
    df = pd.DataFrame(log_entry)

    # check  for already existing file and append
    if os.path.exists(log_file_path):
        df.to_csv(log_file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(log_file_path, index=False)
    
    print(f"✅ {order_type.capitalize()} trade logged successfully!")