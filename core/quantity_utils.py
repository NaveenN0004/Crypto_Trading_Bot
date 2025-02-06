import math # import the math module
from config.settings import DEBUG_MODE # import the DEBUG_MODE from "config/settings.py"


def debug_print(message):

    # debugging info
    if DEBUG_MODE:
        print(message)

def calculate_quantity(investment_amount, current_price, market_details):
    # calculate the quantity based on the investment amount and current price

    # debugging info
    debug_print(f"🔍 Debugging Info: Investment Amount = {investment_amount}, Current Price = {current_price}")

    raw_quantity = investment_amount / current_price  
    debug_print(f"🔍 Debugging Info: Raw Quantity = {raw_quantity}")

    # precision and adjustments
    step = market_details.get("step", 1)
    quantity = math.floor(raw_quantity / step) * step
    debug_print(f"🔍 Debugging Info: Adjusted Quantity (after applying step {step}) = {quantity}")

    # validate calculated quantity
    min_quantity = float(market_details.get("min_quantity", 0))
    max_quantity = float(market_details.get("max_quantity", float("inf")))
    if quantity < min_quantity:
        raise ValueError(f"❗ Investment too low. Min quantity required: {min_quantity}")
    if quantity > max_quantity:
        raise ValueError(f"❗ Investment too high. Max quantity allowed: {max_quantity}")
    
    return quantity