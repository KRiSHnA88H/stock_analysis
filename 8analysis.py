

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

folder = "all_stock_data_divided_ticker_row/Large"
stock_files = os.listdir(folder)

results = []

# ===============================
# STEP 1: Compute metrics
# ===============================
for file in stock_files:
    try:
        df = pd.read_csv(f"{folder}/{file}")

        if len(df) < 2:
            continue

        if "Date" in df.columns:
            df = df.sort_values("Date")

        buy = df.iloc[0]["Close"]
        sell = df.iloc[-1]["Close"]

        ret = (sell - buy) / buy

        df["returns"] = df["Close"].pct_change()
        vol = df["returns"].std()

        profit = sell - buy

        results.append([
            file.replace(".csv", ""),
            ret,
            vol,
            profit
        ])

    except:
        pass

res_df = pd.DataFrame(results, columns=[
    "Stock", "Return", "Volatility", "Profit"
])

res_df = res_df.dropna()

# ==========================================
# 1️⃣ BETTER HISTOGRAM (Profit / Loss Count)
# ==========================================
plt.figure(figsize=(12,6))

plt.hist(res_df["Profit"], bins=40, edgecolor="black")

plt.axvline(0, linestyle="--", linewidth=2)

plt.title("How Many Stocks Gave Profit or Loss")
plt.xlabel("Profit / Loss (Rs)")
plt.ylabel("Number of Stocks")

plt.show()

# ==========================================
# 2️⃣ BETTER RISK vs RETURN
# Bubble size = Profit
# Green = Profit
# Red = Loss
# ==========================================
colors = ["green" if x > 0 else "red" for x in res_df["Profit"]]

sizes = abs(res_df["Profit"]) * 2

plt.figure(figsize=(12,8))

plt.scatter(
    res_df["Volatility"],
    res_df["Return"] * 100,
    s=sizes,
    c=colors,
    alpha=0.6
)

plt.title("Risk vs Return (Bubble = Profit/Loss)")
plt.xlabel("Risk (Volatility)")
plt.ylabel("Return %")

plt.grid(True)
plt.show()

# ==========================================
# 3️⃣ Summary
# ==========================================
profit_count = (res_df["Profit"] > 0).sum()
loss_count = (res_df["Profit"] <= 0).sum()

print("Profit Stocks :", profit_count)
print("Loss Stocks   :", loss_count)
print("Average Return:", round(res_df["Return"].mean()*100,2), "%")