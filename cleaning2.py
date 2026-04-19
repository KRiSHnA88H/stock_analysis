import pandas as pd
import os

folder = "all_stock_data_divided_ticker_row"

# Load and clean the category file
cat = pd.read_csv("EQUITY_L.csv")
cat.columns = cat.columns.str.strip() # Fixes the KeyError from hidden spaces

# Create a 'Blacklist' set for instant lookup (O(1) speed)
# This finds symbols where SERIES is 'BZ' or 'Z'
blacklist = set(cat[cat["SERIES"].str.strip() == "BZ"]["SYMBOL"])

for i in os.listdir(folder):
    subfolder = os.path.join(folder, i)
    if not os.path.isdir(subfolder):
        continue
        
    for j in os.listdir(subfolder):
        file_path = os.path.join(subfolder, j)
        
        # Load the individual stock file
        df = pd.read_csv(file_path)
        print(df.columns)
    
        
        # Ensure the stock file has data and the 'Ticker' column
        if not df.empty and "Ticker" in df.columns:
            ticker = df["Ticker"].iloc[0]
            
            # Check if this ticker is in our BZ blacklist
            if ticker in blacklist:
                print(f"Deleting {ticker} (Series BZ)")
                os.remove(file_path)
        

