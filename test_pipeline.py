import subprocess
import pandas as pd
import joblib

def main():
    # 1. Check data.csv
    try:
        df = pd.read_csv('data.csv')
        print(f"data.csv loaded successfully with {len(df)} rows.")
    except Exception as e:
        print(f"Failed to load data.csv: {e}")
        return

    # 2. Check model.joblib
    try:
        model = joblib.load('model.joblib')
        print("model.joblib loaded successfully.")
    except Exception as e:
        print(f"Failed to load model.joblib: {e}")
        return

    # 3. Test predict.py with data from data.csv
    sample = df.iloc[0]
    odds1, oddsX, odds2 = sample['odds1'], sample['oddsX'], sample['odds2']
    print(f"Testing predict.py with odds: {odds1}, {oddsX}, {odds2}")

    result = subprocess.run(['python3', 'predict.py', str(odds1), str(oddsX), str(odds2)],
                            capture_output=True, text=True)

    if result.returncode == 0:
        print(f"predict.py output: {result.stdout.strip()}")
        if "Predicted Draw Probability:" in result.stdout:
            print("End-to-end validation PASSED.")
        else:
            print("End-to-end validation FAILED: Unexpected output format.")
    else:
        print(f"predict.py FAILED with error: {result.stderr}")

if __name__ == "__main__":
    main()
