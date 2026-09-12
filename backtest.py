import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def run_historical_backtest(historical_df):
    """
    Runs a rolling out-of-sample backtest of the Logistic Regression model 
    predicting 1-month ahead DXY direction.
    """
    try:
        df = historical_df.dropna().copy()
        if len(df) < 36:
            return None, "Insufficient data for 3-year backtesting."

        df['Target'] = (df['dxy'].shift(-1) > df['dxy']).astype(int)
        df = df.iloc[:-1]

        features = ['real_rate', 'yield_spread', 'gdp_growth', 'unemployment']
        
        # Rolling Walk-Forward Backtest (24-month training window)
        predictions = []
        actuals = []
        dates = []

        train_window = 24
        for i in range(train_window, len(df)):
            train_df = df.iloc[:i]
            test_row = df.iloc[[i]]

            scaler = StandardScaler()
            X_train = scaler.fit_transform(train_df[features])
            y_train = train_df['Target']

            X_test = scaler.transform(test_row[features])
            y_test = test_row['Target'].values[0]

            clf = LogisticRegression()
            clf.fit(X_train, y_train)

            pred_prob = clf.predict_proba(X_test)[0][1]
            pred_signal = 1 if pred_prob >= 0.5 else 0

            predictions.append(pred_signal)
            actuals.append(y_test)
            dates.append(test_row.index[0])

        results_df = pd.DataFrame({
            'Date': dates,
            'Predicted_Direction': predictions,
            'Actual_Direction': actuals
        }).set_index('Date')

        results_df['Correct'] = (results_df['Predicted_Direction'] == results_df['Actual_Direction']).astype(int)
        win_rate = results_df['Correct'].mean() * 100
        total_trades = len(results_df)

        return {
            'win_rate': np.round(win_rate, 2),
            'total_trades': total_trades,
            'results_df': results_df
        }, None
    except Exception as e:
        return None, f"Backtest Execution Error: {str(e)}"
