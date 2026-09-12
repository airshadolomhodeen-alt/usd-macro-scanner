def run_macro_analysis(fred_data, dxy_data, news_data):
    if "error" in fred_data:
        return "Error", 0, [f"Data Error: {fred_data['error']}"]
    
    score = 0
    if fred_data["fed_funds"] >= 4.0:
        score += 30
    elif fred_data["fed_funds"] >= 2.0:
        score += 15
        
    if dxy_data["change_1m"] > 0:
        score += 25
    else:
        score -= 25
        
    score += int(news_data["sentiment"] * 25)
    
    if score > 20:
        condition = "Strong Bullish 🚀"
    elif score < -20:
        condition = "Bearish 📉"
    else:
        condition = "Contracting / Range-Bound ↔️"
        
    drivers = [
        f"Federal Funds Rate standing at {fred_data['fed_funds']}%",
        f"US YoY CPI Inflation at {fred_data['cpi_yoy']:.2f}%",
        f"Unemployment Rate at {fred_data['unemployment']}%",
        f"DXY 1-Month Trend: {dxy_data['change_1m']:.2f}%"
    ]
    
    return condition, score, drivers
