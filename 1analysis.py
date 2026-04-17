import os 
import pandas as pd
import numpy as np

unclean_data_folder="all_stock_data_divided"
clean_data_folder="all_stock_data_divided_ticker_row"


all_stock_data_divided=os.listdir(unclean_data_folder)
for i in all_stock_data_divided:
    l=os.listdir(unclean_data_folder+"/"+i)
    for j in l:
        df=pd.read_csv(unclean_data_folder+"/"+i+"/"+j)
        df.drop([0,1],inplace=True)
        df.reset_index(inplace=True)
        df=df.drop("index",axis="columns")
        col=[]
        
        for k in df.columns:
            col.append(k)
        col[0]="Date"
        print(col)
        df.columns=col
        df["Ticker"]=j[0:len(j)-4]
        os.makedirs(clean_data_folder+"/"+i, exist_ok=True)
        df.to_csv(f"{clean_data_folder}/{i}/{j}")
        
    



        

        
       
