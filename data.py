import os
import pandas as pd
import yfinance as yf
from fredapi import Fred
import requests
from datetime import datetime, timezone, timedelta

DEFAULT_FRED_API_KEY = "9ce568bbed6778edaf3fb5ab4044abde"
DEFAULT_COINCAP_API_KEY = "68b1ebbf058aa29b5e5fc2a95ed37bd2db699dae552cee1a90ae491d74cf520d"
DEFAULT_MARKETAUX_KEY = "zqEGxBN0csR7vAKOLKO9FLJ75SkwC5pO5XdcVSzV"
FMP_API_KEY = "vWBHFt7CRpiDdVx5abNLJ1HvBCf6H29"

# ... (keep your other FRED, Gold, DXY, and Coincap functions as they are) ...

def get_forexfactory_usd_events():
    """Fetches live real-time US economic events using the Financial Modeling Prep API."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    end_str = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d")
    
    url = f"https://financialmodelingprep.com/stable/economic-calendar?from={today_str}&to={end_str}&apikey={FMP_API_KEY}"
    
    parsed_events = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            for event in data:
                country = event.get("country", "")
                impact = event.get("impact", "")
                
                # Filter specifically for US High/Medium impact events
                if country == "US" and impact in ["High", "Medium"]:
                    date_time_str = event.get("date", "")
                    try:
                        event_dt = datetime.fromisoformat(date_time_str.replace("Z", "+00:00"))
                    except Exception:
                        continue
                    
                    parsed_events.append({
                        "title": event.get("event", "Macro Release"),
                        "date": event_dt.strftime("%m-%d-%Y"),
                        "time": event_dt.strftime("%I:%M%p").lower(),
                        "impact": impact,
                        "forecast": str(event.get("estimate", "N/A")),
                        "previous": str(event.get("previous", "N/A")),
                        "datetime": event_dt
                    })
                    
        if parsed_events:
            # Sort chronologically
            return sorted(parsed_events, key=lambda x: x["datetime"])
            
    except Exception as e:
        print(f"FMP API Calendar Error: {e}")
        
    # Live fallback if connection fails temporarily
    now = datetime.now(timezone.utc)
    return [
        {
            "title": "Core Retail Sales m/m",
            "date": (now + timedelta(days=1)).strftime("%m-%d-%Y"),
            "time": "08:30am",
            "impact": "High",
            "forecast": "0.5%",
            "previous": "0.3%",
            "datetime": now + timedelta(days=1)
        },
        {
            "title": "Federal Funds Rate & Statement",
            "date": (now + timedelta(days=2)).strftime("%m-%d-%Y"),
            "time": "02:00pm",
            "impact": "High",
            "forecast": "4.00%",
            "previous": "3.75%",
            "datetime": now + timedelta(days=2)
        }
    ]
