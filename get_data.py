import yfinance as yf
import pandas as pd
import os

df = pd.read_csv("classified_stock_name.csv")

for category in df.columns:
    
    folder_path = f"all_stock_data_divided/{category}"
    os.makedirs(folder_path, exist_ok=True)   # create folder
    
    for stock in df[category].dropna():       # skip NaN
        
        data = yf.download(stock, period="10y", interval="1d")
        
        if data.empty:
            continue
        
        data.to_csv(f"{folder_path}/{stock}.csv")