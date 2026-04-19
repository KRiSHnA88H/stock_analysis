import pandas as pd
import os

folder="processed_stock_data"
df=pd.read_csv(f"{folder}/Large/3MINDIA.NS.csv")



for i in os.listdir(folder):
    for j in os.listdir(f"{folder}/{i}"):
        df=pd.read_csv(f"{folder}/{i}/{j}")
        df.dropna(inplace=True)
        df.to_csv(f"{folder}/{i}/{j}")
print(df.info())
print(df.isnull().sum())