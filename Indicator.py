import pandas as pd
import numpy as np
import os

# ===============================
# Indicators
# ===============================
def sma(close, days):
    return close.rolling(days).mean()

def ema(close, days):
    return close.ewm(span=days, adjust=False).mean()

def rsi(close, days=14):
    change = close.diff()

    gain = change.where(change > 0, 0)
    loss = -change.where(change < 0, 0)

    avg_gain = gain.rolling(days).mean()
    avg_loss = loss.rolling(days).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def volatility(close, days=20):
    returns = close.pct_change()
    return returns.rolling(days).std()

# ===============================
# Add indicators
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
    categories = os.listdir(folder)   # e.g. Penny, LargeCap, etc.

    for category in categories:
        category_path = os.path.join(folder, category)

        if not os.path.isdir(category_path):
            continue

        save_folder = os.path.join("indicator_output", category)
        os.makedirs(save_folder, exist_ok=True)

        files = os.listdir(category_path)

        for file in files:
            try:
                path = os.path.join(category_path, file)

                df = add_indicators(path)

                save_path = os.path.join(save_folder, file)
                df.to_csv(save_path, index=False)

                print(file, "done")

            except Exception as e:
                print(file, "error:", e)

# ===============================
# MAIN
# ===============================
folder = "all_stock_data_divided_ticker_row"
process_folder(folder)