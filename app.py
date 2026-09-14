import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data import (
    get_macro_data,
    get_historical_macro_matrix,
    get_gold_spot_data,
    get_dxy_data,
    get_gold_and_forex_data,
    get_coincap_gold_crypto,
    get_forexfactory_usd_events
)
from analyzer import analyze_macro_framework
from stats_engine import run_arima_forecast, calculate_z_scores, run_logistic_regression, run_pca_decomposition
from backtest import run_historical_backtest

st.set_page_config(
    page_title="XAUUSD Macro & Statistical Forecasting Engine",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 XAUUSD / Gold Macro & Statistical Forecasting Engine")
st.markdown("Institutional-grade macro scanning, Z-Score mean-reversion metrics, and walk-forward directional probability models for Gold traders.")

# Sidebar Controls
st.sidebar.header("What-If Scenario Controller")
enable_simulation = st.sidebar.checkbox("Enable Scenario Simulation")

sim_fed_rate, sim_cpi, sim_unemp, sim_gdp, sim_spread = 3.0, 2.0, 4.0, 2.0, 0.0
if enable_simulation:
    st.sidebar.subheader("Adjust Shock Parameters")
    sim_fed_rate = st.sidebar.slider("Fed Funds Rate (%)", 0.0, 8.0, 3.0, 0.25)
    sim_cpi = st.sidebar.slider("CPI Inflation YoY (%)", -1.0, 10.0, 2.0, 0.1)
    sim_unemp = st.sidebar.slider("Unemployment Rate (%)", 1.0, 15.0, 4.0, 0.1)
    sim_gdp = st.sidebar.slider("GDP Growth (%)", -5.0, 8.0, 2.0, 0.1)
    sim_spread = st.sidebar.slider("10Y-2Y Yield Spread", -1.0, 2.0, 0.0, 0.1)

if st.sidebar.button("Run Live Scan") or not enable_simulation:
    with st.spinner("Ingesting macro data from FRED, Goldprice.dev, and executing statistical pipelines..."):
        macro_data, err = get_macro_data()
        if err or not macro_data:
            st.error(f"Macro Data Error: {err}")
            macro_data = {"fed_rate": 3.0, "cpi": 2.0, "unemployment": 4.0, "gdp_growth": 2.0, "yield_spread": 0.0}
        
        if enable_simulation:
            macro_data = {
                "fed_rate": sim_fed_rate,
                "cpi": sim_cpi,
                "unemployment": sim_unemp,
                "gdp_growth": sim_gdp,
                "yield_spread": sim_spread
            }

        dxy_price, dxy_change = get_dxy_data()
        gold_price, gold_change, gold_err = get_gold_spot_data()
        fx_data = get_gold_and_forex_data()
        crypto_data, crypto_err = get_coincap_gold_crypto()
        historical_df, hist_err = get_historical_macro_matrix()

    # Top Metrics Row: XAUUSD, DXY, and Correlated Assets
    st.markdown("---")
    st.subheader("📊 Spot Assets & Core Macro Drivers")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("XAUUSD Spot Price", f"${gold_price:,.2f}", f"{gold_change:+.2f}% (1M)")
    with col2:
        st.metric("DXY Index", f"${dxy_price:,.2f}" if dxy_price else "N/A", f"{dxy_change:+.2f}% (1M)")
    with col3:
        st.metric("Fed Funds Rate", f"{macro_data['fed_rate']:.2f}%")
    with col4:
        st.metric("CPI Inflation (YoY)", f"{macro_data['cpi']:.2f}%")

    # Correlated Forex & PAXG Crypto Bar
    col_fx1, col_fx2, col_crypto = st.columns(3)
    with col_fx1:
        eur_info = fx_data.get("EUR/USD (High Pos-Corr)", {"price": 0, "change": 0})
        st.metric("EUR/USD (Pos-Corr)", f"{eur_info['price']:.4f}", f"{eur_info['change']:+.2f}%")
    with col_fx2:
        aud_info = fx_data.get("AUD/USD (Commodity Pos-Corr)", {"price": 0, "change": 0})
        st.metric("AUD/USD (Pos-Corr)", f"{aud_info['price']:.4f}", f"{aud_info['change']:+.2f}%")
    with col_crypto:
        if crypto_data and isinstance(crypto_data, list) and len(crypto_data) > 0:
            pax = crypto_data[0]
            pax_price = float(pax.get("priceUsd", 0))
            pax_change = float(pax.get("changePercent24Hr", 0))
            st.metric("PAX Gold (PAXG On-Chain)", f"${pax_price:,.2f}", f"{pax_change:+.2f}% (24h)")
        else:
            st.metric("PAX Gold (PAXG On-Chain)", "Feed Restricted", "0.00%")

    # Macro & Statistical Analysis
    analysis = analyze_macro_framework(macro_data, dxy_change)

    st.markdown("---")
    st.subheader("🎯 XAUUSD 3-Month Directional Forecast & Probability Engine")
    
    forecast_col, rec_col = st.columns([1, 1.5])
    with forecast_col:
        st.markdown(f"### Projected Direction: **{analysis['bias']}**")
        st.write(f"**Bullish Probability:** {analysis['bullish_prob']}%")
        st.progress(int(analysis['bullish_prob']))
        st.write(f"**Bearish Probability:** {analysis['bearish_prob']}%")
    with rec_col:
        st.markdown("### Strategic Execution Recommendation")
        st.info(analysis['recommendation'])

    # Z-Scores & Statistical Modules
    if historical_df is not None:
        st.markdown("---")
        st.subheader("📐 Statistical Mean-Reversion & Z-Score Metrics")
        z_scores, z_err = calculate_z_scores(historical_df)
        if z_scores:
            zc1, zc2 = st.columns(2)
            with zc1:
                st.metric("Real Rate Z-Score", f"{z_scores['z_score_real_rate']:.2f} σ", help="Measures standard deviation from historical real interest rate norm.")
            with zc2:
                st.metric("DXY Z-Score", f"{z_scores['z_score_dxy']:.2f} σ", help="Identifies overbought/oversold dollar conditions affecting XAUUSD.")

        # Plotly Chart Visualization
        st.markdown("---")
        st.subheader("📈 Historical Macro & Trend Visualization")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=historical_df.index, y=historical_df['real_rate'], mode='lines', name='Real Interest Rate (%)', line=dict(color='orange', width=2)))
        fig.add_trace(go.Scatter(x=historical_df.index, y=historical_df['fed_rate'], mode='lines', name='Fed Funds Rate (%)', line=dict(color='cyan', width=1.5, dash='dot')))
        fig.update_layout(
            title='Historical Real Interest Rate vs Fed Funds Rate Dynamics',
            xaxis_title='Timeline',
            yaxis_title='Percentage (%)',
            template='plotly_dark',
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Economic Calendar & News Section
    st.markdown("---")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.subheader("📅 High-Impact USD Events")
        events = get_forexfactory_usd_events()
        for ev in events:
            st.markdown(ev)
    with c_col2:
        st.subheader("💡 Macro Economic Framework States")
        st.write(f"* **AD Framework:** {analysis['ad_state']}")
        st.write(f"* **SRAS Pressure:** {analysis['sras_state']}")
        st.write(f"* **LRAS Output Gap:** {analysis['lras_gap']}")
        st.write(f"* **Taylor Rate Gap:** {analysis['rate_gap']:+.2f}%")
