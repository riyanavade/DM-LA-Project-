import pandas as pd
from ml_engine import IPLPredictionEngine

df = pd.read_csv('ipl_dataset_5yr.csv')
engine = IPLPredictionEngine(df)
engine.train_all_models()
preds = engine.generate_2027_predictions()
print('Predicted_Runs sample:', preds['Predicted_Runs'].head(10).tolist())
print('Engine._last_debug keys:', list(getattr(engine, '_last_debug', {}).keys()))
print('Engine._last_debug runs_pred first 10:', getattr(engine, '_last_debug', {}).get('runs_pred')[:10])
