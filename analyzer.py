def analyze_macro_framework(macro_data, dxy_change):
    gdp = macro_data.get("gdp_growth", 2.0)
    cpi = macro_data.get("cpi", 2.0)
    unemp = macro_data.get("unemployment", 4.0)
    spread = macro_data.get("yield_spread", 0.0)
    fed_rate = macro_data.get("fed_rate", 3.0)

    real_rate = fed_rate - cpi
    taylor_rate = cpi + 0.5 * (cpi - 2.0) - 0.5 * (unemp - 4.0) + 2.0
    rate_gap = fed_rate - taylor_rate

    # Macro States
    ad_state = "Overheating / Strong Demand" if (gdp > 2.5 and cpi > 3.0) else ("Moderate Expansion" if gdp > 1.5 else "Weak Demand Growth")
    sras_state = "High Cost-Push Pressure" if cpi > 3.5 else ("Subdued Costs" if cpi < 2.0 else "Balanced Inflation")
    lras_gap = "Positive Output Gap (Tight)" if unemp < 3.8 else ("Labor Slack" if unemp > 4.5 else "Full Employment Potential")

    # XAUUSD Directional Scoring (Gold is inversely sensitive to real rates & DXY strength)
    bullish_score = 0
    if real_rate < 0.0:
        bullish_score += 35
    elif real_rate < 1.0:
        bullish_score += 15
    else:
        bullish_score -= 30

    if rate_gap < -0.5:
        bullish_score += 25
    elif rate_gap > 0.5:
        bullish_score -= 25

    if spread < 0.0:  # Inverted yield curve often drives safe-haven gold demand
        bullish_score += 20

    bullish_prob = max(10, min(90, 50 + (bullish_score / 2)))
    bearish_prob = 100 - bullish_prob

    if bullish_score >= 20:
        forecast_direction = "BULLISH (XAUUSD)"
        bias_symbol = "🚀"
        trade_recommendation = "Favorable macro environment for bullion. Look for dip-buying opportunities on XAUUSD and PAXG. Negative real rates or dovish policy gaps support upside continuation."
    elif bullish_score <= -20:
        forecast_direction = "BEARISH (XAUUSD)"
        bias_symbol = "📉"
        trade_recommendation = "Strong real rate headwinds and resilient DXY create downward pressure on gold. Structure rallies as selling opportunities or protect long positions."
    else:
        forecast_direction = "NEUTRAL / RANGE-BOUND"
        bias_symbol = "↔️"
        trade_recommendation = "Mixed macro signals. Trade key technical support and resistance levels while monitoring upcoming inflation prints."

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
