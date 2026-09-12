import streamlit as st
from data import get_macro_data, get_dxy_data, get_forexfactory_usd_events, get_investing_usd_news
from analyzer import analyze_macro_framework

st.set_page_config(page_title="USD Real-Time Macro Scanner", layout="wide")

st.title("USD Real-Time Macro Scanner")

if st.button("Run Live Scan"):
    with st.spinner("Fetching macro indicators, DXY spot price, and USD news..."):
        macro_metrics, error = get_macro_data()
        dxy_price, dxy_change = get_dxy_data()
        ff_events = get_forexfactory_usd_events()
        investing_news = get_investing_usd_news()

    st.subheader("USD Spot & Core Macro Drivers")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="DXY Spot Price", 
            value=f"${dxy_price:.2f}" if dxy_price > 0 else "N/A", 
            delta=f"{dxy_change:+.2f}% (1M)" if dxy_price > 0 else None
        )
        
    if macro_metrics:
        with col2:
            st.metric(label="Fed Funds Rate", value=f"{macro_metrics['fed_rate']:.2f}%")
        with col3:
            st.metric(label="CPI Inflation (YoY)", value=f"{macro_metrics['cpi']:.2f}%")
        with col4:
            st.metric(label="Unemployment Rate", value=f"{macro_metrics['unemployment']:.1f}%")

        analysis = analyze_macro_framework(macro_metrics, dxy_change)

        st.divider()
        st.subheader("USD 3-Month Directional Forecast & Probability Engine")
        
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.info(f"**Projected USD Direction:** {analysis.get('bias', 'NEUTRAL / RANGE-BOUND ↔️')}")
            
            # Safe rendering with fallback values
            bullish_p = float(analysis.get('bullish_prob', 50))
            bearish_p = float(analysis.get('bearish_prob', 50))
            
            st.write(f"**Bullish Probability:** {bullish_p:.0f}%")
            st.progress(int(bullish_p))
            st.write(f"**Bearish Probability:** {bearish_p:.0f}%")
            
            st.metric("Real Fed Funds Rate", f"{analysis.get('real_rate', 0.0):.2f}%")
            st.metric("Implied Taylor Rule Target Rate", f"{analysis.get('taylor_rate', 0.0):.2f}%")

        with col_b:
            st.markdown("### Strategic Execution Recommendation")
            st.write(analysis.get('recommendation', 'Trade macro range bounds.'))
            
            st.markdown("---")
            st.markdown("### Tactical Trading Guidance")
            bias_str = str(analysis.get('bias', 'NEUTRAL'))
            if "BULLISH" in bias_str:
                st.success("• **Primary Trade:** Long USD/JPY or Short EUR/USD on 4H pullbacks.")
                st.write("• **Macro Driver:** Positive real yields and monetary policy tightness relative to economic slack.")
            elif "BEARISH" in bias_str:
                st.error("• **Primary Trade:** Long EUR/USD or Long Gold (XAU/USD).")
                st.write("• **Macro Driver:** Real yields compressed or policy easing priced in.")
            else:
                st.warning("• **Primary Trade:** Range-trading strategies / Mean-reversion.")
                st.write("• **Macro Driver:** Real interest rate cushion maintains equilibrium without strong momentum.")

        with st.expander("Detailed Macroeconomic Framework (AD / SRAS / LRAS)", expanded=True):
            st.write(f"• **Aggregate Demand (AD):** {analysis.get('ad_state', 'N/A')}")
            st.write(f"• **Short-Run Supply (SRAS):** {analysis.get('sras_state', 'N/A')}")
            st.write(f"• **Capacity vs. LRAS:** {analysis.get('lras_gap', 'N/A')}")
            st.write(f"• **Real GDP Growth (YoY):** {macro_metrics.get('gdp_growth', 2.0):.2f}%")
            st.write(f"• **Yield Curve (10Y-2Y Spread):** {macro_metrics.get('yield_spread', 0.0):.2f}%")
            st.write(f"• **Policy Rate Gap (Actual vs. Taylor):** {analysis.get('rate_gap', 0.0):+.2f}%")
    else:
        st.error(error)

    st.divider()

    # ForexFactory and Investing.com feeds
    st.subheader("USD News & Economic Calendar")
    tab1, tab2 = st.tabs(["ForexFactory Calendar", "Investing.com Breaking News"])

    with tab1:
        st.markdown("### Upcoming USD Economic Events")
        if ff_events:
            for event in ff_events:
                st.markdown(event)
        else:
            st.write("No ForexFactory events loaded.")

    with tab2:
        st.markdown("### USD & Fed Market Headlines")
        if investing_news:
            for item in investing_news:
                st.markdown(f"• [{item['title']}]({item['link']}) — *{item['published']}*")
        else:
            st.write("No USD-specific headlines found at this moment.")
