import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

# ----------------- Linear Algebra Focus -----------------
def calculate_performance_score(df):
    # Performance = (Runs * 0.6) + (Wickets * 25) + (Strike Rate * 0.2)
    # Using matrix formulation
    
    # Extract feature matrix
    # Columns: Runs, Wickets, Strike_Rate
    try:
        X = df[['runs', 'wickets', 'strike_rate']].values
    except KeyError: # Fallback to CSV capitalized column names
        X = df[['Runs', 'Wickets', 'Strike_Rate']].values
        
    weights = np.array([0.6, 25.0, 0.2])
    
    # Dot product: X dot weights
    scores = np.dot(X, weights)
    return scores

def perform_clustering(df):
    """
    Cluster players based on their Performance Score and Economy.
    """
    scores = calculate_performance_score(df)
    
    try:
        economy = df['economy'].values
    except KeyError:
        economy = df['Economy'].values
    
    # Vector form and normalization
    X = np.column_stack((scores, economy))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    clusters = kmeans.fit_predict(X_scaled)
    
    return clusters, X

# ----------------- ML Models -----------------

def train_sold_classification(df):
    """Predict if a player is sold or unsold (Classification)"""
    scores = calculate_performance_score(df)
    df['perf_score'] = scores
    
    # Features: perf_score, matches, age (we don't have age, let's use matches and economy)
    try:
        X = df[['perf_score', 'matches', 'economy']]
        y = df['sold_status'].astype(int)
    except KeyError:
        X = df[['perf_score', 'Matches', 'Economy']]
        y = df['Sold_Status'].astype(int)
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Handle the case where the dataset only has 1 class (e.g., all players are "Sold")
    if len(np.unique(y_train)) < 2:
        from sklearn.dummy import DummyClassifier
        constant_val = y_train.iloc[0] if hasattr(y_train, 'iloc') else y_train[0]
        
        rf_clf = DummyClassifier(strategy='constant', constant=constant_val)
        rf_clf.fit(X_train, y_train)
        y_pred = rf_clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred) if len(y_test) > 0 else 1.0
        
        lr_clf = DummyClassifier(strategy='constant', constant=constant_val)
        lr_clf.fit(X_train, y_train)
        
        return rf_clf, lr_clf, acc
    
    # Random Forest
    rf_clf = RandomForestClassifier(random_state=42)
    rf_clf.fit(X_train, y_train)
    y_pred = rf_clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    # Logistic Regression
    lr_clf = LogisticRegression()
    lr_clf.fit(X_train, y_train)
    
    return rf_clf, lr_clf, acc

def train_price_regression(df):
    """Predict the auction price (Regression)"""
    # Only train on sold players
    try:
        sold_df = df[df['sold_status'] == 1].copy()
    except KeyError:
        sold_df = df[df['Sold_Status'] == 1].copy()
        
    scores = calculate_performance_score(sold_df)
    sold_df['perf_score'] = scores
    
    try:
        X = sold_df[['perf_score', 'matches', 'strike_rate']]
        y = sold_df['auction_price']
    except KeyError:
        X = sold_df[['perf_score', 'Matches', 'Strike_Rate']]
        y = sold_df['Auction_Price']
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    rf_reg = RandomForestRegressor(random_state=42)
    rf_reg.fit(X_train, y_train)
    y_pred = rf_reg.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return rf_reg, mse, r2

def get_player_trend(df, player_name):
    """
    Autoregressive/trend analysis for a specific player based on historical performance score.
    Returns: 'Increase', 'Decrease', or 'Stable'
    """
    try:
        player_data = df[df['player_name'].str.lower() == player_name.lower()].sort_values(by='year')
    except KeyError:
         player_data = df[df['Player_Name'].str.lower() == player_name.lower()].sort_values(by='Year')
         
    if len(player_data) < 2:
        return "Not Enough Data"
        
    scores = calculate_performance_score(player_data)
    
    if scores[-1] > scores[-2] * 1.05:
        return "Increase 📈"
    elif scores[-1] < scores[-2] * 0.95:
        return "Decrease 📉"
    else:
        return "Stable ⚖️"
