def analyze_macro_framework(macro_data, dxy_change):
    gdp = macro_data.get("gdp_growth", 2.0)
    cpi = macro_data.get("cpi", 2.0)
    unemp = macro_data.get("unemployment", 4.0)
    spread = macro_data.get("yield_spread", 0.0)
    fed_rate = macro_data.get("fed_rate", 3.0)

    # 1. Real Interest Rate
    real_rate = fed_rate - cpi

    # 2. Implied Taylor Rule Target Rate
    taylor_rate = cpi + 0.5 * (cpi - 2.0) - 0.5 * (unemp - 4.0) + 2.0
    rate_gap = fed_rate - taylor_rate

    # 3. Macroeconomic Framework Indicators
    if gdp > 2.5 and cpi > 3.0:
        ad_state = "Overheating / Strong Demand Expansion"
    elif gdp < 1.0 and cpi > 3.0:
        ad_state = "Contracting Demand / High Price Pressure"
    elif gdp > 1.5:
        ad_state = "Moderate & Stable Expansion"
    else:
        ad_state = "Weak Demand Growth"

    if cpi > 3.5:
        sras_state = "High Cost-Push Inflationary Pressure"
    elif cpi < 2.0:
        sras_state = "Subdued Production Costs / Low Inflation"
    else:
        sras_state = "Balanced Supply-Side Inflation"

    if unemp < 3.8:
        lras_gap = "Positive Output Gap (Capacity Constraint)"
    elif unemp > 4.5:
        lras_gap = "Negative Output Gap (Labor Capacity Slack)"
    else:
        lras_gap = "Operating Near Full Employment Potential"

    # 4. Score & Probability Calculation
    bullish_score = 0
    
    if real_rate > 1.0:
        bullish_score += 30
    elif real_rate > 0.0:
        bullish_score += 15
    else:
        bullish_score -= 20

    if rate_gap > 0.5:
        bullish_score += 25
    elif rate_gap < -0.5:
        bullish_score -= 25

    if gdp > 2.0 and unemp <= 4.1:
        bullish_score += 25
    elif gdp < 1.2:
        bullish_score -= 20

    if spread > 0.1:
        bullish_score += 20
    elif spread < -0.2:
        bullish_score -= 20

    bullish_prob = max(10, min(90, 50 + (bullish_score / 2)))
    bearish_prob = 100 - bullish_prob

    if bullish_score >= 25:
        forecast_direction = "BULLISH (3M Outlook)"
        bias_symbol = "🚀"
        trade_recommendation = (
            "Look for dip-buying opportunities in USD pairs (e.g., Short EUR/USD, Short GBP/USD). "
            "Positive real rates and growth outperformance support capital inflows into USD assets."
        )
    elif bullish_score <= -25:
        forecast_direction = "BEARISH (3M Outlook)"
        bias_symbol = "📉"
        trade_recommendation = (
            "Reduce long USD exposure or structure rallies as selling opportunities. "
            "Negative real rates or policy easing expectations create macro headwinds for DXY."
        )
    else:
        forecast_direction = "NEUTRAL / RANGE-BOUND"
        bias_symbol = "↔️"
        trade_recommendation = (
            "Trade key technical support and resistance bounds. Current real rate cushion "
            "is insufficient to establish a sustained multi-month trend."
        )

    return {
        "bias": f"{forecast_direction} {bias_symbol}",
        "bullish_prob": bullish_prob,
        "bearish_prob": bearish_prob,
        "recommendation": trade_recommendation,
        "ad_state": ad_state,
        "sras_state": sras_state,
        "lras_gap": lras_gap,
        "real_rate": real_rate,
        "taylor_rate": taylor_rate,
        "rate_gap": rate_gap
    }
