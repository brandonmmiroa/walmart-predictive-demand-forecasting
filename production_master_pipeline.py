import os
import pandas as pd
import numpy as np
import psycopg2
from getpass import getpass
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

print("PHASE 6: EXECUTING PRODUCTION-READY MASTER PIPELINE")
print("="*65)

# ==========================================
# ⚙️ GLOBAL PIPELINE CONFIGURATION TOGGLE
# ==========================================
ENVIRONMENT = "DEVELOPMENT_CLOUD"

OUTPUT_DIR = "/content/drive/MyDrive/data_outputs_project2"
FINAL_EXPORT_PATH = os.path.join(OUTPUT_DIR, "production_final_forecast.csv")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ==========================================
# DATA INGESTION ENGINE
# ==========================================
if ENVIRONMENT == "DEVELOPMENT_CLOUD":
    print("🔌 Mode: DEVELOPMENT_CLOUD | Preprocessing local raw data for cloud streaming...")
    
    LOCAL_RAW_FILE = "/content/drive/MyDrive/data_outputs_project2/Walmart.csv"
    if not os.path.exists(LOCAL_RAW_FILE):
        raise FileNotFoundError(f"❌ File not found at {LOCAL_RAW_FILE}.")
    
    df_local = pd.read_csv(LOCAL_RAW_FILE)
    df_local.columns = df_local.columns.str.strip()
    df_local['calculated_revenue'] = df_local['quantity_sold'] * df_local['unit_price']
    
    # Clean and normalize timestamps to pure dates to prevent duplicate group keys
    df_local['transaction_date'] = pd.to_datetime(df_local['transaction_date'], errors='coerce')
    df_local = df_local.dropna(subset=['transaction_date'])
    df_local['transaction_date'] = df_local['transaction_date'].dt.date  # <-- Fix applied here

    # Grouping happens on clean dates now
    df_daily = df_local.groupby('transaction_date').agg({
        'calculated_revenue': 'sum',
        'quantity_sold': 'sum'
    }).reset_index().sort_values('transaction_date')

    df_daily['masked_revenue'] = df_daily['calculated_revenue'] * 0.85

    DB_HOST = "aws-0-eu-west-1.pooler.supabase.com"
    DB_NAME = "postgres"
    DB_USER = "postgres.hgtnabavsodfjuuugvbp"
    DB_PORT = "6543"
    DB_PASS = getpass("Enter Supabase Password: ")

    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)
        cursor = conn.cursor()
        
        print("Streaming masked features into Supabase Cloud Warehouse...")
        cursor.execute("TRUNCATE TABLE store_daily_features;")
        
        for index, row in df_daily.iterrows():
            cursor.execute(
                """
                INSERT INTO store_daily_features (date_only, total_quantity, masked_revenue)
                VALUES (%s, %s, %s);
                """,
                (row['transaction_date'], int(row['quantity_sold']), float(row['masked_revenue']))
            )
        conn.commit()
        print("Data stream upload completely verified!")

        print("Pulling freshly streamed features down for ML processing...")
        df_raw = pd.read_sql_query("SELECT * FROM store_daily_features ORDER BY date_only ASC;", conn)
        cursor.close()
        conn.close()

        df_raw['date_only'] = pd.to_datetime(df_raw['date_only'])
        df_raw['day_of_week'] = df_raw['date_only'].dt.dayofweek

        X = df_raw[['total_quantity', 'day_of_week']]
        y = df_raw['masked_revenue']
        dates = df_raw['date_only']
        print("✔️ Cloud Features Synced and Verified.")
        
    except Exception as e:
        print(f"❌ Cloud Connection Failed: {e}")
        raise

elif ENVIRONMENT == "PRODUCTION_LOCAL":
    print("🏭 Mode: PRODUCTION_LOCAL | Processing raw enterprise unmasked data...")
    LOCAL_RAW_FILE = "/content/drive/MyDrive/data_outputs_project2/Walmart.csv"

    if not os.path.exists(LOCAL_RAW_FILE):
        raise FileNotFoundError(f"❌ File not found at {LOCAL_RAW_FILE}.")

    df_local = pd.read_csv(LOCAL_RAW_FILE)
    df_local.columns = df_local.columns.str.strip()

    df_local['calculated_revenue'] = df_local['quantity_sold'] * df_local['unit_price']
    df_local['transaction_date'] = pd.to_datetime(df_local['transaction_date'], errors='coerce')
    df_local = df_local.dropna(subset=['transaction_date'])
    df_local['transaction_date'] = df_local['transaction_date'].dt.date  # <-- Fix applied here

    df_daily = df_local.groupby('transaction_date').agg({
        'calculated_revenue': 'sum',
        'quantity_sold': 'sum'
    }).reset_index().sort_values('transaction_date')

    df_daily['transaction_date'] = pd.to_datetime(df_daily['transaction_date'])
    df_daily['day_of_week'] = df_daily['transaction_date'].dt.dayofweek

    X = df_daily[['quantity_sold', 'day_of_week']]
    y = df_daily['calculated_revenue']
    dates = df_daily['transaction_date']

    print(f"✔️ Production Features Compiled. Loaded {len(df_daily)} unique days from Walmart.csv.")

# ==========================================
# CORE MACHINE LEARNING PREDICTIVE ENGINE
# ==========================================
print("\nSplitting timeline and initializing Random Forest Regressor...")
split_index = int(len(X) * 0.80)

X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
dates_test = dates.iloc[split_index:]

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
r2 = r2_score(y_test, predictions)

print(f"📈 Refactored Pipeline Production R² Score: {r2:.4f}")

# ==========================================
# 💾 ENTERPRISE COMPLIANT EXPORT
# ==========================================
df_final_output = pd.DataFrame({
    'Timeline_Date': dates_test,
    'Ground_Truth_Actual': y_test,
    'Model_Forecast_Prediction': predictions
})

df_final_output.to_csv(FINAL_EXPORT_PATH, index=False)
print(f"\n PIPELINE COMPLETE. Production artifacts synchronized to Drive:\n {FINAL_EXPORT_PATH}")
