import os
import pandas as pd

input_root = "all_stock_data_divided_ticker_row"
output_root = "processed_stock_data"

# create output root if not exists
os.makedirs(output_root, exist_ok=True)

for category in os.listdir(input_root):
    input_cat_path = os.path.join(input_root, category)
    output_cat_path = os.path.join(output_root, category)

    os.makedirs(output_cat_path, exist_ok=True)

    for file in os.listdir(input_cat_path):
        file_path = os.path.join(input_cat_path, file)

        df = pd.read_csv(file_path)

        # --- Ensure sorting by date ---
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        # --- Calculate Returns ---
        df["Returns"] = df["Close"].pct_change()

        # --- Equity Curve ---
        df["Equity"] = (df["Returns"] + 1).cumprod()

        # --- Total Return (single value) ---
        total_return = (df["Returns"] + 1).prod() - 1

        # --- Add ticker column ---
        ticker = file.replace(".csv", "")
        df["Ticker"] = ticker

        # --- Add Total Return to ALL rows ---
        df["Total_Return"] = total_return

        # --- Select only required columns ---
        final_df = df[["Date", "Ticker", "Returns", "Equity", "Total_Return"]]

        # --- Save ---
        output_path = os.path.join(output_cat_path, file)
        final_df.to_csv(output_path, index=False)

print("✅ Done processing all stocks!")