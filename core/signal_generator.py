from typing import Tuple
import pandas as pd
from config.settings import DEBUG_MODE

class SignalGenerator:
    
    # analyzes technical indicators from a DataFrame to generate buy/sell signals
    
    def __init__(self) -> None:
        self.required_indicators = [
            "RSI", "MACD", "MACD_Signal", "EMA_9", "EMA_21",
            "BBU", "BBM", "BBL", "Stoch_%K", "Stoch_%D", "Volume"
        ]

    def validate_data(self, df: pd.DataFrame) -> bool:
        # check that all required indicators exist in the DataFrame

        return all(indicator in df.columns for indicator in self.required_indicators)

    def analyze_indicators(self, df: pd.DataFrame) -> Tuple[bool, str]:
        # analyze indicators to determine whether a trade signal is 'buy', 'sell', or 'hold'
        
        try:
            if not self.validate_data(df):
                print("❌ Missing required indicators")
                return False, "hold"

            latest = df.iloc[-1]
            previous = df.iloc[-2]

            if DEBUG_MODE:
                print("\n🔍 Latest Indicator Values:")
                for indicator in self.required_indicators:
                    print(f"{indicator}: {latest[indicator]:.2f}")

            trend_up = (latest['EMA_9'] > latest['EMA_21'] and latest['close'] > latest['EMA_9'])
            trend_down = (latest['EMA_9'] < latest['EMA_21'] and latest['close'] < latest['EMA_9'])
            volume_increasing = latest['Volume'] > previous['Volume'] * 1.2

            rsi_oversold = latest['RSI'] < 30
            rsi_overbought = latest['RSI'] > 70

            macd_crossover = (latest['MACD'] > latest['MACD_Signal'] and previous['MACD'] <= previous['MACD_Signal'])
            macd_crossunder = (latest['MACD'] < latest['MACD_Signal'] and previous['MACD'] >= previous['MACD_Signal'])

            bb_oversold = latest['close'] <= latest['BBL']
            bb_overbought = latest['close'] >= latest['BBU']

            stoch_oversold = latest['Stoch_%K'] < 20
            stoch_overbought = latest['Stoch_%K'] > 80

            if (trend_up and volume_increasing and rsi_oversold and macd_crossover and bb_oversold and stoch_oversold):
                if DEBUG_MODE:
                    print("\n🎯 Buy Signal Conditions Met:")
                    print(f"Trend Up: {trend_up}")
                    print(f"Volume Increasing: {volume_increasing}")
                    print(f"RSI Oversold: {rsi_oversold}")
                    print(f"MACD Crossover: {macd_crossover}")
                    print(f"BB Oversold: {bb_oversold}")
                    print(f"Stochastic Oversold: {stoch_oversold}")
                return True, "buy"
            elif (trend_down and volume_increasing and rsi_overbought and macd_crossunder and bb_overbought and stoch_overbought):
                if DEBUG_MODE:
                    print("\n🎯 Sell Signal Conditions Met:")
                    print(f"Trend Down: {trend_down}")
                    print(f"Volume Increasing: {volume_increasing}")
                    print(f"RSI Overbought: {rsi_overbought}")
                    print(f"MACD Crossunder: {macd_crossunder}")
                    print(f"BB Overbought: {bb_overbought}")
                    print(f"Stochastic Overbought: {stoch_overbought}")
                return True, "sell"
            return False, "hold"
        except Exception as e:
            print(f"❌ Error in signal generation: {e}")
            return False, "error"

    def get_signal_strength(self, df: pd.DataFrame) -> float:        
        # calculate a combined signal strength from several indicators
        # returns a value from 0 to 100
        
        try:
            if not self.validate_data(df):
                return 0.0
            latest = df.iloc[-1]
            rsi_strength = abs(50 - latest['RSI']) / 50
            macd_strength = abs(latest['MACD'] - latest['MACD_Signal'])
            bb_range = (latest['BBU'] - latest['BBM']) if (latest.get('BBU') and latest.get('BBM')) else 1
            bb_strength = abs(latest['close'] - latest['BBM']) / bb_range
            stoch_strength = abs(50 - latest['Stoch_%K']) / 50

            total_strength = (rsi_strength * 0.3 +
                              macd_strength * 0.3 +
                              bb_strength * 0.2 +
                              stoch_strength * 0.2) * 100
            return min(total_strength, 100.0)
        except Exception as e:
            print(f"❌ Error calculating signal strength: {e}")
            return 0.0
