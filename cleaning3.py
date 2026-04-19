import pandas as pd
import os

folder="all_stock_data_divided_ticker_row"
for i in os.listdir(folder):
    subfolder=os.listdir(os.path.join(folder,i))
    for j in subfolder:
        df = pd.read_csv(os.path.join(folder,i,j))
        df.set_index("Date", inplace=True)
        df.drop(columns=["Unnamed: 0"], inplace=True)
        df.to_csv(os.path.join(folder,i,j))