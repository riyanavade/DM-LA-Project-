import pandas as pd
import numpy as np
import os
import random

np.random.seed(42)
random.seed(42)

def generate_multi_year_dataset(base_csv="ipl_dataset.csv", output_csv="ipl_dataset_5yr.csv"):
    if not os.path.exists(base_csv):
        print(f"Error: {base_csv} not found.")
        return None
        
    df_base = pd.read_csv(base_csv)
    df_base = df_base.dropna(how='all')
    
    years = [2022, 2023, 2024, 2025, 2026]
    all_data = []
    
    # Age performance curve
    def age_factor(age):
        return np.exp(-0.5 * ((age - 30) / 5) ** 2)
        
    for _, player in df_base.iterrows():
        base_age = int(player.get('Age', 28))
        role = str(player.get('Role', 'Batsman'))
        nationality = str(player.get('Nationality', 'India'))
        
        base_batting_avg = float(player.get('Batting_Avg', 25.0))
        base_sr = float(player.get('Strike_Rate', 125.0))
        base_econ = float(player.get('Bowling_Economy', 8.0))
        base_wickets = int(player.get('Wickets', 0))
        base_price = float(player.get('Base_Price_CR', 2.0))
        sold_price_base = float(player.get('Sold_Price_CR', 5.0))
        base_year = int(player.get('Year', 2025))
        
        for year in years:
            if year == base_year:
                # Preserve exactly but ensure Matches and Runs exist
                row = player.to_dict()
                row['Year'] = base_year
                
                # If Matches/Runs missing from base dataset or zero, generate them
                matches_val = row.get('Matches')
                runs_val = row.get('Runs')
                
                if pd.isna(matches_val) or matches_val == 0 or matches_val == 0.0:
                    row['Matches'] = max(7, int(np.random.normal(13, 1.5)))
                if pd.isna(runs_val) or runs_val == 0 or runs_val == 0.0:
                    if 'Bowler' in role:
                        row['Runs'] = max(10, int(base_batting_avg * 8 * np.random.uniform(0.3, 0.6)))
                    else:
                        row['Runs'] = max(50, int(base_batting_avg * 12 * np.random.uniform(0.7, 1.0)))
                        
                all_data.append(row)
                continue
                
            year_diff = year - base_year
            current_age = base_age + year_diff
            
            perf_ratio = age_factor(current_age) / max(age_factor(base_age), 0.1)
            noise = 1.0 + np.random.normal(0, 0.05) * abs(year_diff)
            perf_ratio *= noise
            perf_ratio = max(0.5, min(1.5, perf_ratio))
            
            row = {
                'Player_Name': player['Player_Name'],
                'Role': role,
                'Nationality': nationality,
                'Age': current_age,
                'Team': str(player.get('Team', '')),
                'Year': year,
                'Base_Price_CR': round(base_price * (1.0 + 0.05 * year_diff), 2)
            }
            
            # Generating stats
            matches = max(3, min(16, int(np.random.normal(12, 3))))
            row['Matches'] = matches
            
            if 'Batsman' in role or 'Keeper' in role or 'All-Rounder' in role:
                row['Batting_Avg'] = round(base_batting_avg * perf_ratio + np.random.uniform(-4, 4), 1)
                row['Strike_Rate'] = round(base_sr * (0.9 + 0.1 * perf_ratio) + np.random.uniform(-10, 10), 1)
                runs = int(row['Batting_Avg'] * matches * np.random.uniform(0.6, 1.1))
                if 'All-Rounder' in role:
                    runs = int(runs * 0.7)
                row['Runs'] = max(20, runs)
            else:
                row['Batting_Avg'] = round(base_batting_avg * perf_ratio + np.random.uniform(-2, 2), 1)
                row['Strike_Rate'] = round(base_sr * perf_ratio, 1)
                row['Runs'] = max(5, int(row['Batting_Avg'] * matches * 0.4))
                
            row['Batting_Avg'] = max(5.0, row['Batting_Avg'])
            row['Strike_Rate'] = max(60.0, row['Strike_Rate'])
            
            if 'Bowler' in role or 'All-Rounder' in role:
                econ_factor = 1.0 + (1.0 - perf_ratio) * 0.1
                row['Bowling_Economy'] = round(max(5.0, base_econ * econ_factor + np.random.uniform(-0.5, 0.5)), 1)
                wkt_base = base_wickets if base_wickets > 0 else (15 if 'Bowler' in role else 8)
                wkts = int((wkt_base / 14.0) * matches * perf_ratio + np.random.uniform(-3, 5))
                row['Wickets'] = max(1, wkts)
            else:
                row['Bowling_Economy'] = 0.0
                row['Wickets'] = 0
                
            # Auction Price
            inflation = 1.0 + (0.05 * year_diff)
            sold_price = sold_price_base * perf_ratio * inflation * np.random.uniform(0.85, 1.15)
            
            if nationality != 'India':
                sold_price *= np.random.uniform(1.0, 1.2)
                
            row['Sold_Price_CR'] = round(max(row['Base_Price_CR'] * 0.9, min(30.0, sold_price)), 2)
            
            # Status
            if row['Sold_Price_CR'] > row['Base_Price_CR'] and perf_ratio > 0.6:
                row['Status'] = 'Sold'
            else:
                row['Status'] = 'Sold' if random.random() < 0.8 else 'Unsold'
                
            if row['Status'] == 'Unsold':
                row['Sold_Price_CR'] = 0.0
                row['Team'] = ''
                
            all_data.append(row)
            
    df_multi = pd.DataFrame(all_data)
    df_multi.to_csv(output_csv, index=False)
    print(f"Generated {len(df_multi)} records spanning {min(years)} to {max(years)}.")
    return df_multi

if __name__ == "__main__":
    generate_multi_year_dataset()
