import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run_arima_forecast(series_data, steps=3, order=(1, 1, 1)):
    try:
        clean_series = series_data.dropna()
        if len(clean_series) < 24:
            return None, "Insufficient series length for ARIMA."
        model = ARIMA(clean_series, order=order)
        fitted = model.fit()
        return fitted.forecast(steps=steps), None
    except Exception as e:
        return None, f"ARIMA Error: {str(e)}"

def calculate_z_scores(historical_df):
    try:
        df = historical_df.dropna().copy()
        if len(df) < 12:
            return None, "Insufficient data for Z-Scores."
        
        rr = df['real_rate']
        z_rr = (rr.iloc[-1] - rr.mean()) / rr.std() if rr.std() != 0 else 0.0

        dxy = df['dxy']
        z_dxy = (dxy.iloc[-1] - dxy.mean()) / dxy.std() if dxy.std() != 0 else 0.0

        return {"z_score_real_rate": z_rr, "z_score_dxy": z_dxy}, None
    except Exception as e:
        return None, f"Z-Score Error: {str(e)}"

def run_logistic_regression(historical_df):
    try:
        df = historical_df.dropna().copy()
        if len(df) < 30:
            return None, "Dataset too small."
        df['Target'] = (df['dxy'].shift(-1) > df['dxy']).astype(int)
        df = df.iloc[:-1]

        features = ['real_rate', 'yield_spread', 'gdp_growth', 'unemployment']
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df[features])
        y = df['Target']

        clf = LogisticRegression()
        clf.fit(X_scaled, y)
        
        prob_up = clf.predict_proba(scaler.transform(df[features].iloc[[-1]]))[0][1]
        coef_df = pd.DataFrame({'Feature': features, 'Coefficient': clf.coef_[0]})
        return {'prob_up': prob_up * 100, 'coefficients': coef_df}, None
    except Exception as e:
        return None, f"Logistic Regression Error: {str(e)}"

def run_pca_decomposition(historical_df):
    try:
        df = historical_df.dropna().copy()
        features = ['fed_rate', 'cpi', 'unemployment', 'yield_spread', 'gdp_growth']
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df[features])

        pca = PCA(n_components=2)
        pca.fit(X_scaled)
        
        components_df = pd.DataFrame(
            pca.components_, 
            columns=features, 
            index=['PC1 (Rate Factor)', 'PC2 (Growth/Labor Factor)']
        )
        return {'explained_variance': pca.explained_variance_ratio_ * 100, 'components': components_df}, None
    except Exception as e:
        return None, f"PCA Error: {str(e)}"
