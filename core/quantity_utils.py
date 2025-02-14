import math
from config.settings import DEBUG_MODE
from typing import Any, Dict

class QuantityUtils:

    # provides utility methods for calculating the order quantity


    @staticmethod
    def debug_print(message: str) -> None:
        if DEBUG_MODE:
            print(message)

    @staticmethod
    def calculate_quantity(investment_amount: float, current_price: float, market_details: Dict[str, Any]) -> float:        
        # calculate the quantity based on the investment amount and current price
        
        QuantityUtils.debug_print(f"🔍 Investment Amount: {investment_amount}, Current Price: {current_price}")
        
        raw_quantity = investment_amount / current_price  
        QuantityUtils.debug_print(f"🔍 Raw Quantity: {raw_quantity}")
        
        step = market_details.get("step", 1)        
        target_precision = int(market_details.get("target_currency_precision", 0))
        
        quantity = math.floor(raw_quantity / step) * step
        QuantityUtils.debug_print(f"🔍 Adjusted Quantity (after applying step {step}): {quantity}")
        
        if target_precision == 0:
            quantity = math.floor(quantity)
            QuantityUtils.debug_print(f"🔍 Adjusted to integer quantity: {quantity}")
        
        min_quantity = float(market_details.get("min_quantity", 0))
        max_quantity = float(market_details.get("max_quantity", float("inf")))
        
        if quantity < min_quantity:
            raise ValueError(f"❗ Investment too low. Min quantity required: {min_quantity}")
        if quantity > max_quantity:
            raise ValueError(f"❗ Investment too high. Max quantity allowed: {max_quantity}")
        return quantity
