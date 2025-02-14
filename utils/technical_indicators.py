import pandas_ta as ta
import pandas as pd
from config.settings import DEBUG_MODE
from typing import Any

class TechnicalIndicators:
    
    # provides methods to calculate various technical indicators and append them to a DataFrame
    
    @staticmethod
    def calculate(df: pd.DataFrame) -> pd.DataFrame:
        # compute and add technical indicators (RSI, MACD, EMA, Bollinger Bands, ATR, Stochastic Oscillator)
        
        try:
            # calculate Relative Strength Index (RSI)
            df["RSI"] = ta.rsi(df["close"], length=14
                               )
            # calculate Moving Average Convergence Divergence (MACD)
            macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
            if macd is not None:
                df["MACD"] = macd["MACD_12_26_9"]
                df["MACD_Signal"] = macd["MACDs_12_26_9"]
                df["MACD_Histogram"] = macd["MACDh_12_26_9"]
            else:
                df["MACD"] = df["MACD_Signal"] = df["MACD_Histogram"] = None
            
            # calculate Exponential Moving Averages (EMA)
            df["EMA_9"] = ta.ema(df["close"], length=9)
            df["EMA_21"] = ta.ema(df["close"], length=21)
            
            # calculate Bollinger Bands
            bollinger = ta.bbands(df["close"], length=20, std=2)
            if bollinger is not None:
                df["BBL"] = bollinger["BBL_20_2.0"]
                df["BBM"] = bollinger["BBM_20_2.0"]
                df["BBU"] = bollinger["BBU_20_2.0"]
            else:
                df["BBL"] = df["BBM"] = df["BBU"] = None
            
            # calculate Average True Range (ATR)
            df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=14)
            # calculate Stochastic Oscillator
            stoch = ta.stoch(df["high"], df["low"], df["close"], k=14, d=3)
            if stoch is not None:
                df["Stoch_%K"] = stoch["STOCHk_14_3_3"]
                df["Stoch_%D"] = stoch["STOCHd_14_3_3"]
            else:
                df["Stoch_%K"] = df["Stoch_%D"] = None
            
            # pass through volume data
            df["Volume"] = df["volume"]

            if DEBUG_MODE:
                print("🔍 Technical Indicators Calculated:")
                print(df.tail())
            return df
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            return df
