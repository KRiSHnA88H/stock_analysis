# risk.py
# Simple risk analysis for your STOCK_ANALYSIS project

import pandas as pd
import numpy as np
import os


# ===============================
# Max Drawdown
# ===============================
def max_drawdown(close):
    max_price = close.cummax()
    drawdown = (close - max_price) / max_price
    return drawdown.min()


# ===============================
# Volatility
# ===============================
def volatility(close):
    returns = close.pct_change()
    return returns.std() * np.sqrt(252)


# ===============================
# CAGR
# ===============================
def cagr(close):
    days = len(close)

    if days < 2:
        return 0

    total_return = close.iloc[-1] / close.iloc[0]

    years = days / 252

    return (total_return ** (1 / years)) - 1


# ===============================
# Sharpe Ratio
# ===============================
def sharpe(close):
    rf = 0.07

    ret = cagr(close)
    vol = volatility(close)

    if vol == 0:
        return 0

    return (ret - rf) / vol


# ===============================
# Analyze one stock file
# ===============================
def stock_risk(file_path):
    df = pd.read_csv(file_path)

    close = df["Close"]

    return {
        "Stock": os.path.basename(file_path).replace(".csv", ""),
        "CAGR %": round(cagr(close) * 100, 2),
        "Volatility %": round(volatility(close) * 100, 2),
        "Max Drawdown %": round(max_drawdown(close) * 100, 2),
        "Sharpe": round(sharpe(close), 2)
    }


# ===============================
# Full folder analysis
# ===============================
def process_folder(folder):
    files = os.listdir(folder)

    result = []

    for file in files:
        try:
            path = folder + "/" + file

            data = stock_risk(path)

            result.append(data)

            print(file, "done")

        except:
            print(file, "error")

    final = pd.DataFrame(result)

    final = final.sort_values("Sharpe", ascending=False)

    final.to_csv("risk_report.csv", index=False)

    print(final.head(20))


# ===============================
# MAIN
# ===============================
folder = "all_stock_data_divided_ticker_row/Large"

process_folder(folder)