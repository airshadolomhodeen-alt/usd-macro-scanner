from analyzer import analyze_macro_framework

# Call after fetching data
if macro_metrics:
    analysis = analyze_macro_framework(macro_metrics, dxy_change)

    st.divider()
    st.subheader("Institutional Macroeconomic Analysis & Recommendation")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.info(f"**USD Macro Outlook:** {analysis['bias']}")
        st.metric("Real Fed Funds Rate", f"{analysis['real_rate']:.2f}%")
        
    with col_b:
        st.write(f"**Strategic Recommendation:** {analysis['recommendation']}")

    with st.expander("Macroeconomic Framework Indicators (AD / SRAS / LRAS)", expanded=True):
        st.write(f"• **Aggregate Demand (AD):** {analysis['ad_state']}")
        st.write(f"• **Short-Run Supply (SRAS):** {analysis['sras_state']}")
        st.write(f"• **Capacity vs. LRAS:** {analysis['lras_gap']}")
        st.write(f"• **Real GDP Growth (YoY):** {macro_metrics['gdp_growth']:.2f}%")
        st.write(f"• **Yield Curve (10Y-2Y Spread):** {macro_metrics['yield_spread']:.2f}%")
