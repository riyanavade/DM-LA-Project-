import pandas as pd
from generate_sample_data import generate_multi_year_dataset
import ml_engine as mle
import database as db

print("Generating 4-year data...")
generated_df = generate_multi_year_dataset("ipl_dataset.csv", "ipl_dataset_4yr.csv")

print("Generated dataframe columns:", generated_df.columns)

ml_df = generated_df.rename(columns={
    'player_name': 'Player_Name', 'team': 'Team', 'role': 'Role',
    'nationality': 'Nationality', 'age': 'Age', 'matches': 'Matches',
    'runs': 'Runs', 'wickets': 'Wickets', 'strike_rate': 'Strike_Rate',
    'economy': 'Bowling_Economy', 'batting_avg': 'Batting_Avg',
    'year': 'Year', 'auction_price': 'Sold_Price_CR',
    'base_price': 'Base_Price_CR', 'sold_status': 'Status'
})

if 'Status' in ml_df.columns:
    def normalize_status(x):
        s = str(x).strip().lower()
        return 'Sold' if s in ['sold', 'retained', 'trade', '1', 'true', 'yes'] else 'Unsold'
    ml_df['Status'] = ml_df['Status'].apply(normalize_status)

print("Training models...")
engine = mle.IPLPredictionEngine(ml_df)
engine.train_all_models()

print("Generating predictions...")
preds_2026 = engine.generate_next_year_predictions()

print("Predictions df:", preds_2026.head())

mapped_2026 = pd.DataFrame({
    'Player_Name': preds_2026['Player_Name'],
    'Role': preds_2026['Role'],
    'Nationality': preds_2026['Nationality'],
    'Age': preds_2026['Age'],
    'Team': preds_2026['Team'],
    'Year': preds_2026['Year'],
    'Base_Price_CR': preds_2026['Base_Price_CR'],
    'Matches': preds_2026['Predicted_Matches'],
    'Batting_Avg': preds_2026['Predicted_Batting_Avg'],
    'Strike_Rate': preds_2026['Predicted_Strike_Rate'],
    'Runs': preds_2026['Predicted_Runs'],
    'Bowling_Economy': preds_2026['Predicted_Economy'],
    'Wickets': preds_2026['Predicted_Wickets'],
    'Sold_Price_CR': preds_2026['Predicted_Price'],
    'Status': ['Sold' if p > 50 else 'Unsold' for p in preds_2026['Sold_Probability']]
})

print("Combined:")
combined = pd.concat([generated_df, mapped_2026], ignore_index=True)
print(combined.tail())
