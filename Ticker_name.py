import yfinance as yf
import pandas as pd

df = pd.read_csv("EQUITY_L.csv")
# Create the list of tickers
symbols = (df["SYMBOL"] + ".NS").tolist()

# Download current data for all tickers at once
# 'period="1d"' gets the most recent day of trading
for i in symbols:
    data=yf.download(i,period="1d")
    data.to_csv(f"data/{i}.csv")




    
