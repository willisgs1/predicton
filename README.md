# Football Draw Prediction

This project uses historical football odds and match results to predict the probability of a draw.

## Files

- `tests.txt`: Raw historical data containing match results and odds.
- `parse_data.py`: Script to parse `tests.txt` and generate `data.csv`.
- `data.csv`: Cleaned dataset generated from the raw data.
- `train_model.py`: Script to engineer features and train a Logistic Regression model.
- `model.joblib`: The trained model file.
- `predict.py`: Tool to predict draw probability for new matches.
- `test_pipeline.py`: Verification script for the entire pipeline.

## Usage

### 1. Data Parsing
To update the cleaned data from `tests.txt`:
```bash
python3 parse_data.py
```

### 2. Model Training
To retrain the model on the latest data:
```bash
python3 train_model.py
```

### 3. Making Predictions
To predict the draw probability for a match, provide the decimal odds for Home, Draw, and Away:
```bash
python3 predict.py <odds_home> <odds_draw> <odds_away>
```
Example:
```bash
python3 predict.py 2.5 3.2 2.8
```

## Requirements
- pandas
- numpy
- scikit-learn
- joblib
