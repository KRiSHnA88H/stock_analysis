import os
import pandas as pd
import numpy as np

# ================================
# 📊 METRIC FUNCTIONS
# ================================

def calculate_cagr(df):
    n_years = len(df) / 252  # trading days
    if n_years == 0:
        return np.nan
    total_return = df["Close"].iloc[-1] / df["Close"].iloc[0]
    return (total_return ** (1 / n_years) - 1) * 100


def calculate_volatility(df):
    returns = df["Close"].pct_change().dropna()
    returns = returns[returns.abs() < 0.5]  # remove extreme spikes
    if len(returns) == 0:
        return np.nan
    return returns.std() * np.sqrt(252) * 100


def calculate_max_drawdown(df):
    returns = df["Close"].pct_change().fillna(0)
    equity = (1 + returns).cumprod()

    peak = equity.cummax()
    drawdown = (equity - peak) / peak

    return drawdown.min() * 100


def calculate_sharpe(df):
    returns = df["Close"].pct_change().dropna()
    returns = returns[returns.abs() < 0.5]

    if returns.std() == 0 or len(returns) == 0:
        return np.nan

    return (returns.mean() / returns.std()) * np.sqrt(252)


# ================================
# 📂 MAIN PIPELINE
# ================================

base_folder = "all_stock_data_divided_ticker_row"

results = []

for category in os.listdir(base_folder):
    category_path = os.path.join(base_folder, category)

    if not os.path.isdir(category_path):
        continue

    for stock_file in os.listdir(category_path):
        file_path = os.path.join(category_path, stock_file)

        try:
            df = pd.read_csv(file_path)

            # Basic cleaning
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.sort_values("Date")

            df = df[df["Close"] > 0]
            df = df.dropna()

            # Skip very small datasets
            if len(df) < 50:
                continue

            # ====================
            # 📊 CALCULATIONS
            # ====================
            cagr = calculate_cagr(df)
            vol = calculate_volatility(df)
            mdd = calculate_max_drawdown(df)
            sharpe = calculate_sharpe(df)

            results.append({
                "Ticker": stock_file.replace(".csv", ""),
                "Category": category,
                "CAGR %": round(cagr, 2),
                "Volatility %": round(vol, 2),
                "Max Drawdown %": round(mdd, 2),
                "Sharpe": round(sharpe, 2)
            })

            print(f"Processed: {category}/{stock_file}")

        except Exception as e:
            print(f"Error in {file_path}: {e}")

# ================================
# 📈 FINAL OUTPUT
# ================================

summary_df = pd.DataFrame(results)

# Sort (like your example)
summary_df = summary_df.sort_values(by="Sharpe", ascending=False)

# Save
os.makedirs("final_output", exist_ok=True)
summary_df.to_csv("risk_output/risk_merged.csv", index=False)

print("\n✅ DONE — saved to final_output/stock_metrics.csv")
print(summary_df.head(20))