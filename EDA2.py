import pandas as pd

folder="all_stock_data_divided_ticker_row/Large/3MINDIA.NS.csv"
df=pd.read_csv(folder)

print(df.columns)
print(df.info())
print(df.describe())
print(df.isnull().sum())
