import sys
import joblib
import pandas as pd
import numpy as np

def engineer_features(odds1, oddsX, odds2):
    prob1 = 1 / odds1
    probX = 1 / oddsX
    prob2 = 1 / odds2

    sum_probs = prob1 + probX + prob2
    margin = sum_probs - 1
    norm_probX = probX / sum_probs
    odds_diff = np.abs(odds1 - odds2)
    fav_odds = min(odds1, odds2)

    # Return features as a DataFrame with correct names for the pipeline
    return pd.DataFrame([[norm_probX, odds_diff, fav_odds, margin]],
                        columns=['norm_probX', 'odds_diff', 'fav_odds', 'margin'])

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 predict.py <odds_home> <odds_draw> <odds_away>")
        sys.exit(1)

    try:
        odds1 = float(sys.argv[1])
        oddsX = float(sys.argv[2])
        odds2 = float(sys.argv[3])
    except ValueError:
        print("Error: Odds must be numbers.")
        sys.exit(1)

    if odds1 <= 0 or oddsX <= 0 or odds2 <= 0:
        print("Error: Odds must be positive.")
        sys.exit(1)

    try:
        # Load the Pipeline (StandardScaler + LogisticRegression)
        pipeline = joblib.load('model.joblib')
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

    features = engineer_features(odds1, oddsX, odds2)
    probability = pipeline.predict_proba(features)[0][1]

    print(f"Predicted Draw Probability: {probability:.4f}")

if __name__ == "__main__":
    main()
