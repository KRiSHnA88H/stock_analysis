import os
import pandas as pd

folder = "data"
# Using a dictionary to keep categories organized
categories = {
    "Penny": [],
    "Small": [],
    "Mid": [],
    "Large": []
}

# 1. Check if folder exists
if not os.path.exists(folder):
    print(f"Error: Folder '{folder}' not found.")
else:
    for file in os.listdir(folder):
        # Only process CSV files
        if file.endswith(".csv"):
            path = os.path.join(folder, file)
            
            try:
                df = pd.read_csv(path)
                
                # Skip if empty or missing 'Close' column
                if df.empty or "Close" not in df.columns:
                    continue

                # 2. Clean 'Close' column: Remove symbols ($ or ,) and convert to float
                # We use float because stocks often have decimals (e.g., 10.50)
                df['Close'] = pd.to_numeric(
                    df['Close'].astype(str).str.replace(r'[$,]', '', regex=True), 
                    errors='coerce'
                )
                
                # Drop rows where 'Close' couldn't be converted to a number
                df = df.dropna(subset=['Close'])
                
                if df.empty:
                    continue

                # 3. Get the latest price
                price = df["Close"].iloc[-1]    
                stock_name = file.replace(".csv", "")

                # 4. Classification Logic
                if price < 50:
                    categories["Penny"].append(stock_name)
                elif price < 200:
                    categories["Small"].append(stock_name)
                elif price < 1000:
                    categories["Mid"].append(stock_name)
                else:
                    categories["Large"].append(stock_name)
                    
            except Exception as e:
                print(f"Could not process {file}: {e}")

    # 5. Exporting the Data
    # We use from_dict with orient='index' and .T (Transpose) 
    # This aligns the lists into columns even if they have different lengths
    output_df = pd.DataFrame.from_dict(categories, orient='index').transpose()
    
    # Save to CSV (index=False prevents adding an extra row-number column)
    output_df.to_csv("classified_stock_name.csv", index=False)

    print("--- Process Complete ---")
    for cat, items in categories.items():
        print(f"{cat}: {len(items)} stocks found")
    print("Results saved to 'classified_stock_name.csv'")