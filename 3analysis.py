# import pandas as pd
# import matplotlib.pyplot as plt
# import os


# folder="all_stock_data_divided_ticker_row"
# category_of_stock=["Large","Mid","Penny","Small"]
# colors = ["red", "green", "blue","orange"]
# for i in range(len(category_of_stock)):
#     Stock=os.listdir(f"{folder}/{category_of_stock[i]}")
#     for j in Stock:
#         df=pd.read_csv(f"{folder}/{category_of_stock[i]}/{j}")
      
#         plt.plot(df["Date"],df["Open"],color=colors[i])
#         plt.xlabel("Date")
#         plt.ylabel("Open Price")
#         plt.tick_params(axis="x",labelrotation=90)
#         plt.show()
     
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

folder = "all_stock_data_divided_ticker_row"
category_of_stock = ["Large", "Mid", "Penny", "Small"]
colors = ["red", "green", "blue", "orange"]

for i in range(len(category_of_stock)):
    Stock = os.listdir(f"{folder}/{category_of_stock[i]}")
    
    for j in Stock:
        df = pd.read_csv(f"{folder}/{category_of_stock[i]}/{j}")
        
        # ✅ Convert to datetime
        df["Date"] = pd.to_datetime(df["Date"])
        
        fig, ax = plt.subplots()
        
        ax.plot(df["Date"], df["Open"], color=colors[i])
        
        # ✅ Smart tick handling
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        
        plt.xlabel("Date")
        plt.ylabel("Open Price")
        plt.title(j)
        plt.tight_layout()
        plt.show()