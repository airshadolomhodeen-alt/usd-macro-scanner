import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run_arima_forecast(series_data, steps=3, order=(1, 1, 1)):
    """Fits an ARIMA model on a time series and forecasts future steps."""
    try:
        clean_series = series_data.dropna()
        if len(clean_series) < 24:
            return None, "Insufficient time-series length for ARIMA modeling."
            
        model = ARIMA(clean_series, order=order)
        fitted = model.fit()
        forecast = fitted.forecast(steps=steps)
        return forecast, None
    except Exception as e:
        return None, f"ARIMA Convergence Error: {str(e)}"

def run_logistic_regression(historical_df):
    """Trains a Logistic Regression classifier on macro variables to predict next-period DXY direction."""
    try:
        df = historical_df.dropna().copy()
        if len(df) < 30:
            return None, "Dataset too small for Logistic Regression training."

        # Target: 1 if next month DXY is higher, 0 otherwise
        df['Target'] = (df['dxy'].shift(-1) > df['dxy']).astype(int)
        df = df.iloc[:-1]  # drop last row with NaN target

        features = ['real_rate', 'yield_spread', 'gdp_growth', 'unemployment']
        X = df[features]
        y = df['Target']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        clf = LogisticRegression()
        clf.fit(X_scaled, y)

        # Get probability on latest available observation
        latest_observation = scaler.transform(X.iloc[[-1]])
        prob_up = clf.predict_proba(latest_observation)[0][1]

        coef_df = pd.DataFrame({'Feature': features, 'Coefficient': clf.coef_[0]})
        return {'prob_up': prob_up * 100, 'coefficients': coef_df}, None
    except Exception as e:
        return None, f"Logistic Regression Error: {str(e)}"

def run_lda_model(historical_df):
    """Executes Linear Discriminant Analysis (LDA) to classify macro regime."""
    try:
        df = historical_df.dropna().copy()
        if len(df) < 30:
            return None, "Dataset too small for LDA modeling."

        # Define 3 Regimes: 1 = Strong USD, 0 = Neutral USD, -1 = Weak USD
        returns = df['dxy'].pct_change()
        df['Regime'] = 0
        df.loc[returns > 0.01, 'Regime'] = 1
        df.loc[returns < -0.01, 'Regime'] = -1
        df = df.dropna()

        features = ['real_rate', 'yield_spread', 'gdp_growth']
        X = df[features]
        y = df['Regime']

        lda = LinearDiscriminantAnalysis()
        lda.fit(X, y)

        latest_observation = X.iloc[[-1]]
        predicted_regime = lda.predict(latest_observation)[0]
        regime_probs = lda.predict_proba(latest_observation)[0]

        return {
            'regime': predicted_regime,
            'probabilities': regime_probs,
            'classes': lda.classes_
        }, None
    except Exception as e:
        return None, f"LDA Model Error: {str(e)}"

def run_pca_decomposition(historical_df):
    """Extracts principal components across macro parameters to explain market variance."""
    try:
        df = historical_df.dropna().copy()
        features = ['fed_rate', 'cpi', 'unemployment', 'yield_spread', 'gdp_growth']
        X = df[features]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        pca = PCA(n_components=2)
        pca.fit(X_scaled)

        explained_var = pca.explained_variance_ratio_ * 100
        components_df = pd.DataFrame(pca.components_, columns=features, index=['PC1 (Rate Factor)', 'PC2 (Growth/Labor Factor)'])

        return {
            'explained_variance': explained_var,
            'components': components_df
        }, None
    except Exception as e:
        return None, f"PCA Error: {str(e)}"
