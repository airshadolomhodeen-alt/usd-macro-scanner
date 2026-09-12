def analyze_macro_framework(macro_data, dxy_change):
    gdp = macro_data.get("gdp_growth", 2.0)
    cpi = macro_data.get("cpi", 2.0)
    unemp = macro_data.get("unemployment", 4.0)
    spread = macro_data.get("yield_spread", 0.0)
    fed_rate = macro_data.get("fed_rate", 3.0)

    # 1. Macroeconomic State Assessment
    if gdp > 2.5 and cpi > 3.0:
        ad_state = "Overheating / Expansionary AD (Demand-pull pressure)"
        sras_state = "Input Cost Pressure Rising (Upward SRAS shifts)"
    elif gdp < 1.0 and cpi > 3.0:
        ad_state = "Contracting Demand / Stagnant Real Output"
        sras_state = "Stagflationary Shift (SRAS shifting left)"
    else:
        ad_state = "Moderate Aggregate Demand Alignment"
        sras_state = "Stable Supply Conditions"

    # 2. Output Gap relative to LRAS (Unemployment vs NAIRU ~4.0%)
    if unemp < 3.8:
        lras_gap = "Positive Output Gap (Y > Y_potential) — Tight labor market"
    elif unemp > 4.5:
        lras_gap = "Negative Output Gap (Y < Y_potential) — Slack in capacity"
    else:
        lras_gap = "At Potential Output (Y ≈ Y_potential)"

    # 3. Policy Alignment & Final USD Outlook
    real_rate = fed_rate - cpi
    if real_rate > 1.0 and spread > -0.2:
        bias = "BULLISH USD 🚀"
        recommendation = "Maintain Long USD positions or favor USD pairs (e.g., Short EUR/USD). Tight monetary stance with stable growth supports capital inflows."
    elif real_rate < 0 or spread < -0.5:
        bias = "BEARISH USD 📉"
        recommendation = "Reduce USD exposure. Negative real interest rates or inverted yield curves signal economic deceleration and potential policy easing."
    else:
        bias = "NEUTRAL / RANGE-BOUND ↔️"
        recommendation = "Trade ranges. Macro factors balance each other without a clear directional driver."

    return {
        "bias": bias,
        "recommendation": recommendation,
        "ad_state": ad_state,
        "sras_state": sras_state,
        "lras_gap": lras_gap,
        "real_rate": real_rate
    }
