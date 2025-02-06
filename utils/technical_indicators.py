import pandas_ta as ta
from config.settings import DEBUG_MODE


def calculate_indicators(df):

    try:
        # calculate RSI (Relative Strength Index)
        df["RSI"] = ta.rsi(df["close"], length=14)
        
        # calculate MACD (Moving Average Convergence Divergence)
        macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
        if macd is not None:
            df["MACD"] = macd["MACD_12_26_9"]
            df["MACD_Signal"] = macd["MACDs_12_26_9"]
            df["MACD_Histogram"] = macd["MACDh_12_26_9"]
        else:
            df["MACD"] = None
            df["MACD_Signal"] = None
            df["MACD_Histogram"] = None
        
        # calculate EMA (Exponential Moving Average)
        df["EMA_9"] = ta.ema(df["close"], length=9)
        df["EMA_21"] = ta.ema(df["close"], length=21)

        # calculate Bollinger Bands
        bollinger_bands = ta.bbands(df["close"], length=20, std=2)
        if bollinger_bands is not None:
            df["BBL"] = bollinger_bands["BBL_20_2.0"]
            df["BBM"] = bollinger_bands["BBM_20_2.0"]
            df["BBU"] = bollinger_bands["BBU_20_2.0"]
        else:
            df["BBL"] = None
            df["BBM"] = None
            df["BBU"] = None
        
        # calculate ATR (Average True Range)
        df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=14)
        
        # calculate Stochastic Oscillator
        stochastic = ta.stoch(df["high"], df["low"], df["close"], k=14, d=3)
        if stochastic is not None:
            df["Stoch_%K"] = stochastic["STOCHk_14_3_3"]
            df["Stoch_%D"] = stochastic["STOCHd_14_3_3"]
        else:
            df["Stoch_%K"] = None
            df["Stoch_%D"] = None
        
        # calculate Volume Analysis
        df["Volume"] = df["volume"]
        
        if DEBUG_MODE:
            print("🔍 Technical Indicators Calculated:")
            print(df.tail())  # print the last few rows for debugging
        
        return df
    except Exception as e:
        print(f"❌ Error calculating indicators: {e}")
        return df