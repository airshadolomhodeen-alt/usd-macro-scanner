import streamlit as st
from data import (
    get_macro_data, 
    get_dxy_data, 
    get_forexfactory_usd_events, 
    get_investing_usd_news
)
from analyzer import analyze_macro_framework

st.set_page_config(page_title="USD Real-Time Macro Scanner", layout="wide")

st.title("USD Real-Time Macro Scanner")

if st.button("Run Live Scan"):
    with st.spinner("Fetching macro indicators, DXY spot price, and USD news..."):
        # 1. Fetch FRED Macro Indicators
        macro_metrics, error = get_macro_data()
        
        # 2. Fetch DXY Spot Data
        dxy_price, dxy_change = get_dxy_data()
        
        # 3. Fetch News Feeds
        ff_events = get_forexfactory_usd_events()
        investing_news = get_investing_usd_news()

    st.subheader("USD Macro Condition")
    
    # Render Metrics in Columns
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

        # 4. Run Analysis Engine
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
    else:
        st.error(error)

    st.divider()

    # Render Side-by-Side News Tabs
    st.subheader("USD News & Economic Calendar")
    tab1, tab2 = st.tabs(["ForexFactory Calendar", "Investing.com Breaking News"])

    with tab1:
        st.markdown("### Upcoming USD Economic Events")
        for event in ff_events:
            st.markdown(event)

    with tab2:
        st.markdown("### USD & Fed Market Headlines")
        if investing_news:
            for item in investing_news:
                st.markdown(f"• [{item['title']}]({item['link']}) — *{item['published']}*")
        else:
            st.write("No USD-specific headlines found at this moment.")
