# indicators.py
# Simple technical indicators for your STOCK_ANALYSIS project

import pandas as pd
import numpy as np
import os


# ===============================
# Moving Average
# ===============================
def sma(close, days):
    return close.rolling(days).mean()


# ===============================
# Exponential Moving Average
# ===============================
def ema(close, days):
    return close.ewm(span=days, adjust=False).mean()


# ===============================
# RSI
# ===============================
def rsi(close, days=14):
    change = close.diff()

    gain = change.where(change > 0, 0)
    loss = -change.where(change < 0, 0)

    avg_gain = gain.rolling(days).mean()
    avg_loss = loss.rolling(days).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# ===============================
# Volatility
# ===============================
def volatility(close, days=20):
    returns = close.pct_change()
    return returns.rolling(days).std()


# ===============================
# Add indicators to one file
# ===============================
def add_indicators(file_path):
    df = pd.read_csv(file_path)

    df["SMA20"] = sma(df["Close"], 20)
    df["SMA50"] = sma(df["Close"], 50)

    df["EMA12"] = ema(df["Close"], 12)
    df["EMA26"] = ema(df["Close"], 26)

    df["RSI"] = rsi(df["Close"])

    df["Volatility"] = volatility(df["Close"])

    return df


# ===============================
# Process full folder
# ===============================
def process_folder(folder):
    files = os.listdir(folder)

    save_folder = "indicator_output"
    os.makedirs(save_folder, exist_ok=True)

    for file in files:
        try:
            path = folder + "/" + file

            df = add_indicators(path)

            df.to_csv(save_folder + "/" + file, index=False)

            print(file, "done")

        except:
            print(file, "error")


# ===============================
# MAIN
# ===============================
folder = "all_stock_data_divided_ticker_row/Large"

process_folder(folder)