import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler


def _ensure_numeric_column(df, names, default=0.0, dtype=float):
    for name in names:
        if name in df.columns:
            return pd.to_numeric(df[name], errors='coerce').fillna(default).astype(dtype)
    return pd.Series(np.full(len(df), default), index=df.index, dtype=dtype)


def build_features(df):
    """
    Generate 10 advanced engineered features from the raw dataset.
    Handles missing Runs/Matches by inferring values from batting and role information.
    """
    df = df.copy()

    # Normalize incoming column names and fill missing numeric fields.
    df['Age'] = _ensure_numeric_column(df, ['Age', 'age'], default=25.0)
    df['Batting_Avg'] = _ensure_numeric_column(df, ['Batting_Avg', 'batting_avg'], default=20.0)
    df['Strike_Rate'] = _ensure_numeric_column(df, ['Strike_Rate', 'strike_rate'], default=100.0)
    df['Bowling_Economy'] = _ensure_numeric_column(df, ['Bowling_Economy', 'economy', 'bowling_economy'], default=8.0)
    df['Runs'] = _ensure_numeric_column(df, ['Runs', 'runs'], default=np.nan)
    df['Wickets'] = _ensure_numeric_column(df, ['Wickets', 'wickets'], default=np.nan)
    df['Matches'] = _ensure_numeric_column(df, ['Matches', 'matches'], default=np.nan)

    # When core batting or match history is missing, infer stable defaults.
    default_matches = np.where(df['Age'] < 28, 14.0, np.where(df['Age'] < 33, 12.0, 10.0))
    df['Matches'] = df['Matches'].fillna(pd.Series(default_matches, index=df.index))

    # Infer Runs if not present using batting average, role, and matches.
    if df['Runs'].isna().any() or (df['Runs'] == 0).all():
        role_factor = np.where(
            df.get('Role', '').astype(str).str.contains('Bowler', case=False, na=False), 0.35,
            np.where(df.get('Role', '').astype(str).str.contains('All-Rounder', case=False, na=False), 0.65, 0.85)
        )
        inferred_runs = (df['Batting_Avg'] * df['Matches'] * role_factor).round().astype(int)
        df['Runs'] = df['Runs'].fillna(inferred_runs).clip(lower=0)

    # Infer Wickets for non-batsmen if missing.
    if df['Wickets'].isna().any():
        bowler_mask = df.get('Role', '').astype(str).str.contains('Bowler|All-Rounder', case=False, na=False)
        inferred_wickets = np.where(bowler_mask, np.round(df['Matches'] * 0.9).astype(int), 0)
        df['Wickets'] = df['Wickets'].fillna(pd.Series(inferred_wickets, index=df.index)).clip(lower=0)

    # Sort by player and year to allow rolling calculations.
    if 'Year' not in df.columns and 'year' in df.columns:
        df['Year'] = df['year']
    df = df.sort_values(by=['Player_Name', 'Year']).reset_index(drop=True)

    # 1. player_role_score
    role_weights = {'All-Rounder': 1.5, 'Wicket-Keeper Batsman': 1.3, 'Batsman': 1.2, 'Bowler': 1.1, 'Unknown': 1.0}
    df['player_role_score'] = df.get('Role', '').map(role_weights).fillna(1.0)

    # 2. nationality_impact (Overseas premium)
    df['nationality_impact'] = np.where(df.get('Nationality', '').astype(str) == 'India', 1.0, 1.25)

    # 3. age_factor (Gaussian curve peaking at 29)
    df['age_factor'] = np.exp(-0.5 * ((df['Age'] - 29) / 5) ** 2)

    # 4. batting_average_score (Normalized)
    df['batting_average_score'] = df['Batting_Avg'] / max(df['Batting_Avg'].max(), 1.0)

    # 5. consistency_score (Rolling mean / std of runs/wickets)
    runs_mean = df.groupby('Player_Name')['Runs'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    runs_std = df.groupby('Player_Name')['Runs'].transform(lambda x: x.rolling(3, min_periods=1).std().fillna(1))
    df['consistency_score'] = np.where(runs_mean > 0, runs_mean / (runs_std + 1), 0)

    # 6. recent_form (Row-wise operation)
    df['recent_form'] = df['Runs'] * 0.7 + df['Wickets'] * 15 * 0.7

    # 7. performance_growth (Year over Year change)
    perf = df['Runs'] + df['Wickets'] * 20
    df['performance_growth'] = perf.groupby(df['Player_Name']).pct_change().fillna(0).clip(-1, 2)

    # 8. strike_rate_trend (Difference from rolling mean)
    sr_mean = df.groupby('Player_Name')['Strike_Rate'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    df['strike_rate_trend'] = df['Strike_Rate'] - sr_mean

    # 9. economy_trend (Difference from rolling mean, inverted)
    econ_mean = df.groupby('Player_Name')['Bowling_Economy'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    df['economy_trend'] = econ_mean - df['Bowling_Economy']

    # 10. experience_score (Cumulative matches)
    df['experience_score'] = df.groupby('Player_Name')['Matches'].cumsum() / 15.0 # normalized loosely

    return df

def encode_categoricals(df):
    """Encode categorical columns for ML models."""
    df = df.copy()
    le = LabelEncoder()
    cat_cols = ['Role', 'Nationality', 'Team', 'Player_Name']
    for col in cat_cols:
        if col in df.columns:
            df[f'{col}_Encoded'] = le.fit_transform(df[col].astype(str))
            
    # Binary encoding for Status
    if 'Status' in df.columns:
        df['Sold_Status_Num'] = np.where(df['Status'].astype(str).str.lower().isin(['sold', 'retained', 'trade']), 1, 0)
    
    return df

def get_feature_matrix(df, targets=None):
    """Select the final feature matrix for modeling."""
    df_encoded = encode_categoricals(build_features(df))
    
    features = [
        'Age', 'Matches', 'player_role_score', 'nationality_impact', 'age_factor',
        'batting_average_score', 'consistency_score', 'recent_form', 
        'performance_growth', 'strike_rate_trend', 'economy_trend', 'experience_score',
        'Role_Encoded', 'Nationality_Encoded', 'Base_Price_CR'
    ]
    
    # Keep only available features
    features = [f for f in features if f in df_encoded.columns]
    
    X = df_encoded[features].astype(float).fillna(0)
    
    if targets:
        # Cast targets to numeric where possible, or float
        Y = df_encoded[targets].apply(pd.to_numeric, errors='coerce').fillna(0)
        return X, Y, df_encoded
    return X, df_encoded
