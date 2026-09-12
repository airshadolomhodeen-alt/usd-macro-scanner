import os
import yfinance as yf
from fredapi import Fred
import feedparser
from textblob import TextBlob

def get_fred_metrics():
    api_key = os.environ.get("FRED_API_KEY", "")
    if not api_key:
        return {"error": "Missing FRED API Key"}
    
    try:
        fred = Fred(api_key=api_key)
        fed_funds = fred.get_series("FEDFUNDS").iloc[-1]
        cpi = fred.get_series("CPIAUCSL")
        cpi_yoy = ((cpi.iloc[-1] - cpi.iloc[-13]) / cpi.iloc[-13]) * 100
        unrate = fred.get_series("UNRATE").iloc[-1]
        
        return {
            "fed_funds": float(fed_funds),
            "cpi_yoy": float(cpi_yoy),
            "unemployment": float(unrate)
        }
    except Exception as e:
        return {"error": str(e)}

def get_dxy_market_data():
    try:
        ticker = yf.Ticker("DX-Y.NYB")
        hist = ticker.history(period="1m")
        spot = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[0]
        pct_change = ((spot - prev) / prev) * 100
        return {"spot": float(spot), "change_1m": float(pct_change)}
    except Exception as e:
        return {"spot": 0.0, "change_1m": 0.0}

def get_macro_news_sentiment():
    try:
        feed = feedparser.parse("https://feeds.finance.yahoo.com/rss/2.0/headline?s=DX-Y.NYB")
        sentiments = []
        titles = []
        for entry in feed.entries[:5]:
            blob = TextBlob(entry.title)
            sentiments.append(blob.sentiment.polarity)
            titles.append(entry.title)
        
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        return {"sentiment": avg_sentiment, "headlines": titles}
    except Exception as e:
        return {"sentiment": 0.0, "headlines": []}
