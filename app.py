import streamlit as st
from data import get_fred_metrics, get_dxy_market_data, get_macro_news_sentiment
from analyzer import run_macro_analysis

st.set_page_config(page_title="USD Macro Condition Scanner", layout="wide")

st.title("USD Real-Time Macro Scanner")

if st.button("Run Live Scan", type="primary"):
    with st.spinner("Fetching macro data & computing scores..."):
        fred_data = get_fred_metrics()
        dxy_data = get_dxy_market_data()
        news_data = get_macro_news_sentiment()
        
        condition, score, drivers = run_macro_analysis(fred_data, dxy_data, news_data)
        
        st.subheader("USD Macro Condition")
        if "Bullish" in condition:
            st.success(f"{condition} (Score: {score})")
        elif "Bearish" in condition:
            st.error(f"{condition} (Score: {score})")
        else:
            st.warning(f"{condition} (Score: {score})")
            
        col1, col2, col3, col4 = st.columns(4)
        if "error" not in fred_data:
            col1.metric("DXY Spot Price", f"${dxy_data['spot']:.2f}", f"{dxy_data['change_1m']:.2f}%")
            col2.metric("Fed Funds Rate", f"{fred_data['fed_funds']}%")
            col3.metric("CPI Inflation (YoY)", f"{fred_data['cpi_yoy']:.2f}%")
            col4.metric("Unemployment Rate", f"{fred_data['unemployment']}%")
            
        st.subheader("Key Macro Drivers")
        for driver in drivers:
            st.write(f"- {driver}")
            
        if news_data["headlines"]:
            st.subheader("Recent Headlines")
            for h in news_data["headlines"]:
                st.write(f"• {h}")
