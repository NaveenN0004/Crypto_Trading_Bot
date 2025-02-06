def validate_investment_amount(investment_amount):
    # ensures the investment amount is above the minimum threshold
    
    MIN_INVESTMENT = 100  # minimum investment amount
    if investment_amount < MIN_INVESTMENT:
        raise ValueError(f"⚠️ Investment amount must be at least {MIN_INVESTMENT} INR.")
    return investment_amount


def calculate_risk_management(entry_price, stop_loss_percentage, risk_reward_ratio):
    # calculate stop-loss and take-profit levels
    try:
        stop_loss_price = entry_price * (1 - stop_loss_percentage)
        take_profit_price = entry_price * (1 + stop_loss_percentage * risk_reward_ratio)
        return {
            "stop_loss_price": round(stop_loss_price, 9),
            "take_profit_price": round(take_profit_price, 9),
        }
    except Exception as e:
        print(f"❌ Error in calculate_risk_management: {e}")
        return None