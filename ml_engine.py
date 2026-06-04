import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score
import feature_engineering as fe

def evaluate_regressors(X_train, X_test, y_train, y_test):
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'Decision Tree': DecisionTreeRegressor(random_state=42),
        'Linear Regression': LinearRegression()
    }
    
    results = []
    best_model = None
    best_r2 = -float('inf')
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        
        results.append({'Model': name, 'RMSE': rmse, 'MAE': mae, 'R2': r2})
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            
    return pd.DataFrame(results), best_model

def evaluate_classifiers(X_train, X_test, y_train, y_test):
    # Handle single-class scenarios to prevent XGBoost / sklearn crashes
    if len(np.unique(y_train)) < 2:
        from sklearn.dummy import DummyClassifier
        constant_val = y_train.iloc[0] if hasattr(y_train, 'iloc') else y_train.values[0] if hasattr(y_train, 'values') else y_train[0]
        
        dummy = DummyClassifier(strategy='constant', constant=constant_val)
        dummy.fit(X_train, y_train)
        preds = dummy.predict(X_test)
        acc = accuracy_score(y_test, preds) if len(y_test) > 0 else 1.0
        
        results = [{'Model': 'Dummy Classifier (Single Class)', 'Accuracy': acc}]
        return pd.DataFrame(results), dummy

    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000)
    }
    
    results = []
    best_model = None
    best_acc = -1
    
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)
            
            results.append({'Model': name, 'Accuracy': acc})
            if acc > best_acc:
                best_acc = acc
                best_model = model
        except Exception:
            continue
            
    # Fallback if all models fail
    if best_model is None:
        from sklearn.dummy import DummyClassifier
        best_model = DummyClassifier(strategy='most_frequent')
        best_model.fit(X_train, y_train)
        results.append({'Model': 'Fallback Dummy', 'Accuracy': 0.0})
            
    return pd.DataFrame(results), best_model

class IPLPredictionEngine:
    def __init__(self, df):
        self.raw_df = df
        self.targets = ['Runs', 'Wickets', 'Sold_Price_CR', 'Sold_Status_Num']
        self.X, self.Y, self.processed_df = fe.get_feature_matrix(df, self.targets)
        self.models = {}
        self.metrics = {}
        
    def _safe_split(self, X, y):
        """Handle train/test split safely for very small datasets."""
        n = len(X)
        if n < 5:
            # Too small to split meaningfully - use all data for both train and test
            return X, X, y, y
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def train_all_models(self):
        # Predict Runs
        X_train, X_test, y_train, y_test = self._safe_split(self.X, self.Y['Runs'])
        res_runs, best_runs = evaluate_regressors(X_train, X_test, y_train, y_test)
        self.models['Runs'] = best_runs
        self.metrics['Runs'] = res_runs
        
        # Predict Wickets
        X_train, X_test, y_train, y_test = self._safe_split(self.X, self.Y['Wickets'])
        res_wkt, best_wkt = evaluate_regressors(X_train, X_test, y_train, y_test)
        self.models['Wickets'] = best_wkt
        self.metrics['Wickets'] = res_wkt
        
        # Predict Price
        X_train, X_test, y_train, y_test = self._safe_split(self.X, self.Y['Sold_Price_CR'])
        res_price, best_price = evaluate_regressors(X_train, X_test, y_train, y_test)
        self.models['Price'] = best_price
        self.metrics['Price'] = res_price
        
        # Predict Sold Status
        X_train, X_test, y_train, y_test = self._safe_split(self.X, self.Y['Sold_Status_Num'])
        res_sold, best_sold = evaluate_classifiers(X_train, X_test, y_train, y_test)
        self.models['Sold'] = best_sold
        self.metrics['Sold'] = res_sold
        
    def generate_2027_predictions(self):
        # Create a proxy for 2027 using latest data (2026 if available)
        latest_year = self.processed_df['Year'].max()
        df_latest = self.processed_df[self.processed_df['Year'] == latest_year].copy()
        
        # Increment age and year
        df_latest['Age'] += (2027 - latest_year)
        df_latest['Year'] = 2027
        
        # Get features
        X_2027, _ = fe.get_feature_matrix(df_latest)
        
        # Predict
        runs_pred = self.models['Runs'].predict(X_2027)
        wkts_pred = self.models['Wickets'].predict(X_2027)
        price_pred = self.models['Price'].predict(X_2027)

        # Attach debug info for interactive inspection
        try:
            self._last_debug = {
                'X_2027_columns': list(X_2027.columns) if hasattr(X_2027, 'columns') else None,
                'X_2027_sample': X_2027.head(5).to_dict(orient='list') if hasattr(X_2027, 'head') else None,
                'runs_pred': runs_pred.tolist() if hasattr(runs_pred, 'tolist') else list(runs_pred),
                'wkts_pred': wkts_pred.tolist() if hasattr(wkts_pred, 'tolist') else list(wkts_pred),
                'price_pred': price_pred.tolist() if hasattr(price_pred, 'tolist') else list(price_pred)
            }
        except Exception:
            self._last_debug = None
        
        # Safely handle predict_proba - DummyClassifier with 1 class returns only 1 column
        try:
            if hasattr(self.models['Sold'], "predict_proba"):
                proba = self.models['Sold'].predict_proba(X_2027)
                if proba.shape[1] >= 2:
                    sold_prob = proba[:, 1]
                else:
                    # Only 1 class known - use the single column as probability
                    sold_prob = proba[:, 0]
            else:
                sold_prob = self.models['Sold'].predict(X_2027).astype(float)
        except Exception:
            # Ultimate fallback - assume all sold with 80% probability
            sold_prob = np.ones(len(X_2027)) * 0.8
            
        results = pd.DataFrame({
            'Player_Name': df_latest['Player_Name'],
            'Role': df_latest['Role'],
            'Predicted_Runs': np.maximum(0, runs_pred.astype(int)),
            'Predicted_Wickets': np.maximum(0, wkts_pred.astype(int)),
            'Predicted_Price': np.maximum(0.5, np.round(price_pred, 2)),
            'Sold_Probability': np.round(sold_prob * 100, 2)
        })
        
        # Price bounds
        results['Price_Min'] = np.maximum(0.5, results['Predicted_Price'] * 0.8)
        results['Price_Max'] = results['Predicted_Price'] * 1.2
        results['Unsold_Probability'] = 100 - results['Sold_Probability']
        
        return results

if __name__ == "__main__":
    # Test
    df = pd.read_csv('ipl_dataset_5yr.csv')
    engine = IPLPredictionEngine(df)
    engine.train_all_models()
    preds = engine.generate_2027_predictions()
    print(preds.head())
