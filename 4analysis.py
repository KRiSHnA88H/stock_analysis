import pandas as pd
import os
import matplotlib.pyplot as plt


# what if bought all penny stocks....
stock=os.listdir("all_stock_data_divided_ticker_row/Penny")
diff=[]

for i in stock:
    df=pd.read_csv(f"all_stock_data_divided_ticker_row/Penny/{i}")
    buy=df.loc[0,"Close"]
    sell=df.iloc[-1]["Close"]
    diff.append((sell-buy)/buy)
    
plt.figure(figsize=(40,20))
colors = ["green" if x > 0 else "red" for x in diff]
plt.bar(stock, diff,color=colors)

plt.xlabel("Stock")
plt.ylabel("Profit / Loss")
plt.title("Penny Stocks Profit if Bought at Start and Sold at End")

plt.xticks(rotation=90,fontsize=5)
plt.show()
    
ticker=[]
returns = []
vol_list = []

for i in stock:
    
    df = pd.read_csv(f"all_stock_data_divided_ticker_row/Penny/{i}")
    ticker.append(df["Ticker"][0])
    buy = df.loc[0, "Close"]
    sell = df.iloc[-1]["Close"]
    ret = (sell - buy) / buy
    
    df["returns"] = df["Close"].pct_change()
    vol = df["returns"].std()
    
    returns.append(ret)
    vol_list.append(vol)

plt.scatter(vol_list, returns,label=ticker)

plt.xlabel("Risk (Volatility)")
plt.ylabel("Return")
plt.title("Risk vs Return (Penny Stocks)")


plt.show()