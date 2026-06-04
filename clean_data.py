import pandas as pd
import numpy as np

def clean_dataset(file_path="ipl_dataset.csv"):
    try:
        # Load dataset
        df = pd.read_csv(file_path)
        print(f"Original shape: {df.shape}")
        
        # 1. Remove duplicates
        initial_len = len(df)
        df.drop_duplicates(inplace=True)
        print(f"Removed {initial_len - len(df)} duplicate rows.")
        
        # 2. Handle missing values
        # For numerical columns, fill with median; for categorical, fill with mode
        num_cols = df.select_dtypes(include=[np.number]).columns
        cat_cols = df.select_dtypes(exclude=[np.number]).columns
        
        for col in num_cols:
            if df[col].isnull().sum() > 0:
                print(f"Filling missing values in numerical column: {col}")
                df[col] = df[col].fillna(df[col].median())
                
        for col in cat_cols:
            if df[col].isnull().sum() > 0:
                print(f"Filling missing values in categorical column: {col}")
                df[col] = df[col].fillna(df[col].mode()[0])
                
        # 3. Handle anomalies (e.g., negative values in stats)
        stats_cols = ['Matches', 'Runs', 'Wickets', 'Strike_Rate', 'Economy', 'Auction_Price']
        for col in stats_cols:
            if col in df.columns:
                anomalies = df[df[col] < 0]
                if len(anomalies) > 0:
                    print(f"Fixing {len(anomalies)} negative values in {col} (Setting to 0).")
                    df.loc[df[col] < 0, col] = 0
        
        # 4. Standardize column names (optional, but good practice)
        # Uncomment if you want to enforce lowercase column names
        # df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
        
        # Save the cleaned dataset
        df.to_csv(file_path, index=False)
        print(f"Cleaned dataset saved to {file_path}. New shape: {df.shape}")
        
    except Exception as e:
        print(f"Error occurred during data cleaning: {e}")

if __name__ == "__main__":
    clean_dataset()
