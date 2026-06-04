import os
import sys
import pandas as pd

# Update imports to match existing functions
import database as db
from generate_sample_data import generate_multi_year_dataset

def main():
    print("="*50)
    print("INITIALIZING IPL 2027 PREDICTION PIPELINE")
    print("="*50)
    
    # 1. Database Migration
    print("\n[1/5] Migrating Database Schema...")
    db.init_db()  # init_db now calls migrate_db()
    print("Database schema ready.")
    
    # 2. Generate Data
    print("\n[2/5] Generating 5-Year Dataset (2022-2026)...")
    df = generate_multi_year_dataset("ipl_dataset.csv", "ipl_dataset_5yr.csv")
    if df is None:
        print("Data generation failed. Ensure ipl_dataset.csv exists.")
        sys.exit(1)
    
    # 3. Upload Data to DB
    print("\n[3/5] Uploading Data to MySQL...")
    db.clear_all_data()
    db.upload_data_to_db(df)
    print("Data uploaded successfully.")
    
    # 4. Feature Engineering & ML is handled in app.py now (caching), 
    # but let's do a quick validation run
    print("\n[4/5] Validating ML Engine & Features...")
    import ml_engine as ml
    engine = ml.IPLPredictionEngine(df)
    engine.train_all_models()
    preds = engine.generate_2027_predictions()
    print(f"ML Engine validated. Generated {len(preds)} predictions.")
    
    # 5. Launch Streamlit
    print("\n[5/5] Launching Streamlit Application...")
    os.system("python run_app.py")

if __name__ == "__main__":
    main()
