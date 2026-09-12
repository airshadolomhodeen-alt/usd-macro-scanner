import os
import pandas as pd
import yfinance as yf
from fredapi import Fred
import feedparser

def get_fred_client():
    """Retrieves FRED API key safely from environment or secrets."""
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("FRED_API_KEY", "")
        except Exception:
            pass
    
    # Strip any trailing whitespace or control characters
    cleaned_key = api_key.strip() if api_key else ""
    if not cleaned_key:
        return None
    return Fred(api_key=cleaned_key)

def get_macro_data():
    """Fetches key macro indicators from FRED."""
    fred = get_fred_client()
    if not fred:
        return None, "FRED_API_KEY missing or invalid."

    try:
        # Fetch FRED Series
        fed_rate = fred.get_series('FEDFUNDS').dropna().iloc[-1]
        cpi = fred.get_series('CPIAUCSL').pct_change(12).dropna().iloc[-1] * 100
        unemployment = fred.get_series('UNRATE').dropna().iloc[-1]

        return {
            "fed_rate": fed_rate,
            "cpi": cpi,
            "unemployment": unemployment
        }, None
    except Exception as e:
        return None, f"FRED Error: {str(e)}"

def get_dxy_data():
    """Fetches real-time price and 1-month trend for DXY."""
    # DX-Y.NYB is the primary Yahoo Finance ticker for the US Dollar Index
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
    """Pulls current high-impact USD economic calendar events."""
    # Reliable XML/RSS endpoint for calendar data
    url = "https://www.forexfactory.com/ff_calendar_thisweek.xml"
    events = []
    
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get('title', '')
            country = entry.get('country', '') or entry.get('currency', '')
            
            # Filter specifically for USD items
            if "USD" in country.upper() or "USD" in title.upper():
                date_str = entry.get('date', 'Upcoming')
                time_str = entry.get('time', '')
                events.append(f"• **{title}** — {date_str} {time_str}")
                
            if len(events) >= 5:
                break
    except Exception as e:
        events.append(f"• Could not load ForexFactory calendar: {str(e)}")
        
    if not events:
        events.append("• No immediate USD calendar events scheduled.")
        
    return events

def get_investing_usd_news():
    """Pulls breaking Forex and USD market news from Investing.com RSS."""
    url = "https://www.investing.com/rss/news_1.rss"
    news = []
    
    try:
        # User-agent header prevents basic anti-bot blocks
        feed = feedparser.parse(url, agent="Mozilla/5.0")
        
        # USD-related keywords to filter articles
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
        print(f"Investing.com RSS Error: {e}")
        
    return news
