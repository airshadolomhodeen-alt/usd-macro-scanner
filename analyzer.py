def analyze_macro_framework(macro_data, dxy_change):
    gdp = macro_data.get("gdp_growth", 2.0)
    cpi = macro_data.get("cpi", 2.0)
    unemp = macro_data.get("unemployment", 4.0)
    spread = macro_data.get("yield_spread", 0.0)
    fed_rate = macro_data.get("fed_rate", 3.0)

    # Calculate Real Fed Funds Rate
    real_rate = fed_rate - cpi

    # Aggregate Demand Assessment
    if gdp > 2.5 and cpi > 3.0:
        ad_state = "Overheating / Strong Demand Expansion"
    elif gdp < 1.0 and cpi > 3.0:
        ad_state = "Contracting Demand / High Price Pressure"
    elif gdp > 1.5:
        ad_state = "Moderate & Stable Expansion"
    else:
        ad_state = "Weak Demand Growth"

    # SRAS Assessment
    if cpi > 3.5:
        sras_state = "High Cost-Push Inflationary Pressure"
    elif cpi < 2.0:
        sras_state = "Subdued Production Costs / Low Inflation"
    else:
        sras_state = "Balanced Supply-Side Inflation"

    # LRAS Gap Assessment (NAIRU ~ 4.0%)
    if unemp < 3.8:
        lras_gap = "Positive Output Gap (Capacity Constraint)"
    elif unemp > 4.5:
        lras_gap = "Negative Output Gap (Labor Capacity Slack)"
    else:
        lras_gap = "Operating Near Full Employment Potential"

    # Strategic Currency Guidance
    if real_rate > 1.0 and spread > -0.2:
        bias = "BULLISH USD 🚀"
        recommendation = "Maintain Long USD exposure or target rallies against lower-yielding currencies. Real yields remain restrictive and growth holds steady."
    elif real_rate < 0.0 or spread < -0.5:
        bias = "BEARISH USD 📉"
        recommendation = "Reduce USD exposure or seek Short opportunities. Yield curve inversion or negative real rates indicate policy headwinds."
    else:
        bias = "NEUTRAL / RANGE ↔️"
        recommendation = "Trade macro range bounds. Counterbalancing economic drivers provide no immediate multi-week bias."

    return {
        "bias": bias,
        "recommendation": recommendation,
        "ad_state": ad_state,
        "sras_state": sras_state,
        "lras_gap": lras_gap,
        "real_rate": real_rate
    }
