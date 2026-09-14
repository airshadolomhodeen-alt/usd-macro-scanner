import os
import pandas as pd
import yfinance as yf
from fredapi import Fred
import feedparser
import requests

# Embedded API Keys for direct fallback
DEFAULT_FRED_API_KEY = "9ce568bbed6778edaf3fb5ab4044abde"
DEFAULT_COINCAP_API_KEY = "68b1ebbf058aa29b5e5fc2a95ed37bd2db699dae552cee1a90ae491d74cf520d"

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
            "fed_rate": fed_rate,
            "cpi": cpi,
            "unemployment": unemployment,
            "gdp_growth": gdp,
            "yield_spread": yield_spread
        }, None
    except Exception as e:
        return None, f"FRED Error: {str(e)}"

def get_historical_macro_matrix():
    """Fetches full historical time series matrix for statistical modeling."""
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

def get_dxy_data():
    tickers_to_try = ["DX-Y.NYB", "DX=F"]
    for ticker_symbol in tickers_to_try:
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="1mo")
            if not hist.empty and len(hist) > 1:
                current_price = hist['Close'].iloc[-1]
                start_price = hist['Close'].iloc[0]
                pct_change = ((current_price - start_price) / start_price) * 100
                return current_price, pct_change
        except Exception:
            continue
    return 0.0, 0.0

def get_forexfactory_usd_events():
    url = "https://www.forexfactory.com/ff_calendar_thisweek.xml"
    events = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get('title', '')
            country = entry.get('country', '') or entry.get('currency', '')
            if "USD" in country.upper() or "USD" in title.upper():
                date_str = entry.get('date', 'Upcoming')
                time_str = entry.get('time', '')
                events.append(f"• **{title}** — {date_str} {time_str}")
            if len(events) >= 5:
                break
    except Exception as e:
        events.append(f"• Calendar parsing temporarily unavailable: {str(e)}")
    if not events:
        events.append("• No immediate high-impact USD economic events scheduled for today.")
    return events

def get_investing_usd_news():
    url = "https://www.investing.com/rss/news_1.rss"
    news = []
    try:
        feed = feedparser.parse(url, agent="Mozilla/5.0")
        usd_keywords = ["USD", "DOLLAR", "FED", "FOMC", "GREENBACK", "POWELL", "TREASURY", "INFLATION"]
        for entry in feed.entries:
            title = entry.get('title', '')
            link = entry.get('link', '#')
            published = entry.get('published', 'Recent')
            if any(kw in title.upper() for kw in usd_keywords):
                news.append({
                    "title": title,
                    "link": link,
                    "published": published
                })
            if len(news) >= 5:
                break
    except Exception as e:
        print(f"Investing RSS Error: {e}")
    return news

def get_coincap_data(limit=5):
    api_key = ""
    try:
        import streamlit as st
        api_key = st.secrets.get("COINCAP_API_KEY", "")
    except Exception:
        pass
    
    if not api_key:
        api_key = os.getenv("COINCAP_API_KEY", "")

    if not api_key:
        api_key = DEFAULT_COINCAP_API_KEY

    if not api_key:
        return None, "CoinCap API key missing."

    url = f"https://rest.coincap.io/v3/assets?limit={limit}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", []), None
    except Exception as e:
        return None, f"CoinCap API Error: {str(e)}"
