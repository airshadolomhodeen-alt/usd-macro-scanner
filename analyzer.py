import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run_arima_forecast(series_data, steps=3, order=(1, 1, 1)):
    """Fits an ARIMA model on a continuous time series and forecasts future periods."""
    try:
        clean_series = series_data.dropna()
        if len(clean_series) < 24:
            return None, "Insufficient time-series length (minimum 24 monthly periods required)."
            
        model = ARIMA(clean_series, order=order)
        fitted = model.fit()
        forecast = fitted.forecast(steps=steps)
        return forecast, None
    except Exception as e:
        return None, f"ARIMA Convergence Error: {str(e)}"

def run_logistic_regression(historical_df):
    """Trains a Logistic Regression classifier on standardized macro variables to predict next-period DXY direction."""
    try:
        df = historical_df.dropna().copy()
        if len(df) < 30:
            return None, "Dataset too small for Logistic Regression training (minimum 30 rows required)."

        # Target: 1 if next month DXY closes higher, 0 otherwise
        df['Target'] = (df['dxy'].shift(-1) > df['dxy']).astype(int)
        df = df.iloc[:-1]  # Drop last row with incomplete target

        features = ['real_rate', 'yield_spread', 'gdp_growth', 'unemployment']
        X = df[features]
        y = df['Target']

        # Apply StandardScaler to equalize feature variances and resolve zero-coefficient bug
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        clf = LogisticRegression()
        clf.fit(X_scaled, y)

        # Get directional probability on latest observation
        latest_observation = scaler.transform(X.iloc[[-1]])
        prob_up = clf.predict_proba(latest_observation)[0][1]

        # Standardized Beta Coefficients
        coef_df = pd.DataFrame({
            'Feature': features, 
            'Standardized Impact (Beta)': np.round(clf.coef_[0], 4)
        })
        return {'prob_up': prob_up * 100, 'coefficients': coef_df}, None
    except Exception as e:
        return None, f"Logistic Regression Error: {str(e)}"

def run_lda_model(historical_df):
    """Executes Linear Discriminant Analysis (LDA) to classify macro regime."""
    try:
        df = historical_df.dropna().copy()
        if len(df) < 30:
            return None, "Dataset too small for LDA modeling."

        # Define Regimes: 1 = Strong USD, 0 = Neutral/Range, -1 = Weak USD
        returns = df['dxy'].pct_change()
        df['Regime'] = 0
        df.loc[returns > 0.01, 'Regime'] = 1
        df.loc[returns < -0.01, 'Regime'] = -1
        df = df.dropna()

        features = ['real_rate', 'yield_spread', 'gdp_growth']
        X = df[features]
        y = df['Regime']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        lda = LinearDiscriminantAnalysis()
        lda.fit(X_scaled, y)

        latest_observation = scaler.transform(X.iloc[[-1]])
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
    """Extracts principal components across macro parameters to isolate key structural drivers."""
    try:
        df = historical_df.dropna().copy()
        features = ['fed_rate', 'cpi', 'unemployment', 'yield_spread', 'gdp_growth']
        X = df[features]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        pca = PCA(n_components=2)
        pca.fit(X_scaled)

        explained_var = pca.explained_variance_ratio_ * 100
        components_df = pd.DataFrame(
            pca.components_, 
            columns=features, 
            index=['PC1 (Policy & Rate Factor)', 'PC2 (Growth & Labor Factor)']
        )

        return {
            'explained_variance': explained_var,
            'components': np.round(components_df, 4)
        }, None
    except Exception as e:
        return None, f"PCA Error: {str(e)}"
