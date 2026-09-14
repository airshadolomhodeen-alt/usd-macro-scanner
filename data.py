import os
import pandas as pd
import yfinance as yf
from fredapi import Fred
import feedparser
import requests

# Embedded API Keys & Fallbacks
DEFAULT_FRED_API_KEY = "9ce568bbed6778edaf3fb5ab4044abde"
DEFAULT_COINCAP_API_KEY = "68b1ebbf058aa29b5e5fc2a95ed37bd2db699dae552cee1a90ae491d74cf520d"
DEFAULT_GOLD_API_KEY = "ga_live_iv4A7LyCltJP3_BwdLAJMhlp4azEFdyrSXA5rSEc"

def get_fred_client():
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("FRED_API_KEY", "")
        except Exception:
            pass
    if not api_key:
        api_key = DEFAULT_FRED_API_KEY
    
    cleaned_key = api_key.strip() if api_key else ""
    if not cleaned_key:
        return None
    return Fred(api_key=cleaned_key)

def get_macro_data():
    fred = get_fred_client()
    if not fred:
        return None, "FRED_API_KEY missing or invalid."

    try:
        fed_rate = fred.get_series('FEDFUNDS').dropna().iloc[-1]
        cpi = fred.get_series('CPIAUCSL').pct_change(12).dropna().iloc[-1] * 100
        unemployment = fred.get_series('UNRATE').dropna().iloc[-1]
        
        try:
            gdp_series = fred.get_series('GDPC1').pct_change(4).dropna()
            gdp = gdp_series.iloc[-1] * 100 if not gdp_series.empty else 2.0
        except Exception:
            gdp = 2.0
            
        try:
            spread_series = fred.get_series('T10Y2Y').dropna()
            yield_spread = spread_series.iloc[-1] if not spread_series.empty else 0.0
        except Exception:
            yield_spread = 0.0

        return {
            "fed_rate": float(fed_rate),
            "cpi": float(cpi),
            "unemployment": float(unemployment),
            "gdp_growth": float(gdp),
            "yield_spread": float(yield_spread)
        }, None
    except Exception as e:
        return None, f"FRED Error: {str(e)}"

def get_historical_macro_matrix():
    fred = get_fred_client()
    if not fred:
        return None, "FRED API key missing."
    
    try:
        fed_rate = fred.get_series('FEDFUNDS')
        cpi_raw = fred.get_series('CPIAUCSL')
        cpi = cpi_raw.pct_change(12) * 100
        unemp = fred.get_series('UNRATE')
        spread = fred.get_series('T10Y2Y')
        
        dxy = yf.download("DX-Y.NYB", period="5y", interval="1mo", progress=False)['Close']
        if isinstance(dxy, pd.DataFrame):
            dxy = dxy.squeeze()

        df = pd.DataFrame({
            'fed_rate': fed_rate,
            'cpi': cpi,
            'unemployment': unemp,
            'yield_spread': spread
        }).dropna()

        df['real_rate'] = df['fed_rate'] - df['cpi']
        df['gdp_growth'] = 2.1
        
        dxy.index = dxy.index.tz_localize(None)
        df = df.resample('ME').last()
        df['dxy'] = dxy.reindex(df.index, method='ffill')

        return df.dropna(), None
    except Exception as e:
        return None, f"Historical Fetch Error: {str(e)}"

def get_gold_spot_data():
    api_key = os.getenv("GOLD_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GOLD_API_KEY", "")
        except Exception:
            pass
    if not api_key:
        api_key = DEFAULT_GOLD_API_KEY

    # Primary check via yfinance gold futures/spot proxy for absolute chart reliability
    try:
        ticker = yf.Ticker("GC=F")
        hist = ticker.history(period="1mo")
        if not hist.empty and len(hist) > 1:
            current = float(hist['Close'].iloc[-1])
            start = float(hist['Close'].iloc[0])
            change = ((current - start) / start) * 100
            return current, change, None
    except Exception:
        pass
    return 0.0, 0.0, "Spot Gold feed fallback active."

def get_dxy_data():
    for ticker_symbol in ["DX-Y.NYB", "DX=F"]:
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="1mo")
            if not hist.empty and len(hist) > 1:
                current = float(hist['Close'].iloc[-1])
                start = float(hist['Close'].iloc[0])
                return current, ((current - start) / start) * 100
        except Exception:
            continue
    return 0.0, 0.0

def get_gold_and_forex_data():
    assets = {
        "EUR/USD (High Pos-Corr)": "EURUSD=X",
        "AUD/USD (Commodity Pos-Corr)": "AUDUSD=X"
    }
    results = {}
    for name, ticker_symbol in assets.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="1mo")
            if not hist.empty and len(hist) > 1:
                c = float(hist['Close'].iloc[-1])
                s = float(hist['Close'].iloc[0])
                results[name] = {"price": c, "change": ((c - s) / s) * 100}
            else:
                results[name] = {"price": 0.0, "change": 0.0}
        except Exception:
            results[name] = {"price": 0.0, "change": 0.0}
    return results

def get_coincap_gold_crypto(limit=1):
    api_key = os.getenv("COINCAP_API_KEY", DEFAULT_COINCAP_API_KEY)
    url = "https://rest.coincap.io/v3/assets/pax-gold"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json().get("data")
        return [data] if isinstance(data, dict) else data, None
    except Exception as e:
        return None, f"CoinCap API Error: {str(e)}"

def get_forexfactory_usd_events():
    url = "https://www.forexfactory.com/ff_calendar_thisweek.xml"
    events = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get('title', '')
            country = entry.get('country', '') or entry.get('currency', '')
            if "USD" in country.upper() or "USD" in title.upper():
                events.append(f"• **{title}** — {entry.get('date', 'Upcoming')} {entry.get('time', '')}")
            if len(events) >= 5:
                break
    except Exception:
        events.append("• Calendar parsing temporarily unavailable.")
    return events or ["• No immediate high-impact USD events scheduled."]
