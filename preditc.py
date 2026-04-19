import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import json

# ===============================
# LOAD MODEL + FEATURES
# ===============================
model = joblib.load("models/stock_lr.pkl")

with open("models/stock_lr_meta.json", "r") as f:
    feature_cols = json.load(f)["features"]

# ===============================
# INPUT TICKER
# ===============================
ticker = input("Enter stock ticker (e.g. RELIANCE.NS): ").strip()

# ===============================
# FETCH DATA
# ===============================
df = yf.download(ticker, period="6mo", interval="1d")

if df.empty:
    print("❌ No data found")
    exit()

df.reset_index(inplace=True)

# ===============================
# FEATURE ENGINEERING
# ===============================
df["Returns"] = df["Close"].pct_change()
df["SMA20"] = df["Close"].rolling(20).mean()
df["SMA50"] = df["Close"].rolling(50).mean()
df["EMA12"] = df["Close"].ewm(span=12).mean()
df["EMA26"] = df["Close"].ewm(span=26).mean()

# RSI
delta = df["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df["RSI"] = 100 - (100 / (1 + rs))

# Volatility
df["Volatility"] = df["Returns"].rolling(20).std()

# ===============================
# GET prev VALID ROW
# ===============================
df = df.dropna()

if df.empty:
    print("❌ Not enough data")
    exit()

prev=df.iloc[-2]
lastest = df.iloc[-1]

# ===============================
# PREDICTION
# ===============================
X = prev[feature_cols].values.reshape(1, -1)
pred_return = model.predict(X)[0]

# ===============================
# ACTUAL VALUE (prev RETURN)
# ===============================
actual_return = lastest["Returns"].iloc[-1]


# ===============================
# OUTPUT
# ===============================
print("\n📊 RESULT")
print(f"Ticker: {ticker}")
print(f"Predicted Next Return: {pred_return:.4f} ({pred_return*100:.2f}%)")
print(f"Actual Return: {actual_return:.4f} ({actual_return*100:.2f}%)")

# Predicted next price
pred_price = prev["Close"].iloc[-1] * (1 + pred_return)

print(f"Current Price: {lastest['Close'].iloc[-1]:.2f}")
print(f"Predicted Next Price: {pred_price:.2f}")