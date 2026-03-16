import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import joblib

def engineer_features(df):
    # Implied probabilities
    df['prob1'] = 1 / df['odds1']
    df['probX'] = 1 / df['oddsX']
    df['prob2'] = 1 / df['odds2']

    # Margin
    df['margin'] = df['prob1'] + df['probX'] + df['prob2'] - 1

    # Normalized implied probability for draw
    df['norm_probX'] = df['probX'] / (df['prob1'] + df['probX'] + df['prob2'])

    # Absolute difference between home and away odds
    df['odds_diff'] = np.abs(df['odds1'] - df['odds2'])

    # Favorite odds (minimum of home and away)
    df['fav_odds'] = df[['odds1', 'odds2']].min(axis=1)

    return df[['norm_probX', 'odds_diff', 'fav_odds', 'margin']]

def main():
    df = pd.read_csv('data.csv')

    X = engineer_features(df)
    y = df['is_draw']

    # Split data to evaluate performance
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a pipeline with scaling and logistic regression
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegression())
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"Log Loss: {log_loss(y_test, y_prob):.4f}")

    # Retrain on full data for the final model
    pipeline.fit(X, y)

    joblib.dump(pipeline, 'model.joblib')
    print("Model trained on full data and saved to model.joblib")

if __name__ == "__main__":
    main()
