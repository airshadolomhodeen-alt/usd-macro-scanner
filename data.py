# Add to data.py inside get_macro_data()
gdp = fred.get_series('GDPC1').pct_change(4).dropna().iloc[-1] * 100  # Real GDP YoY Growth
yield_spread = fred.get_series('T10Y2Y').dropna().iloc[-1]            # 10Y minus 2Y Spread

return {
    "fed_rate": fed_rate,
    "cpi": cpi,
    "unemployment": unemployment,
    "gdp_growth": gdp,
    "yield_spread": yield_spread
}, None
