import pandas as pd

folder="all_stock_data_divided/Large/3MINDIA.NS.csv"

df=pd.read_csv(folder)

print(df.info())
print(df.describe())
print(df.columns)




