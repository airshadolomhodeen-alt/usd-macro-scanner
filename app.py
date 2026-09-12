import streamlit as st
from data import get_macro_data, get_dxy_data, get_forexfactory_usd_events, get_investing_usd_news, get_historical_macro_matrix
from analyzer import analyze_macro_framework
from stats_engine import run_arima_forecast, run_logistic_regression, run_lda_model, run_pca_decomposition
from backtest import run_historical_backtest

st.set_page_config(page_title="USD Real-Time Macro Scanner", layout="wide")

st.title("USD Real-Time Macro Scanner")

# --- SIDEBAR: "WHAT-IF" SCENARIO SIMULATOR ---
st.sidebar.header("🕹️ What-If Scenario Controller")
enable_scenario = st.sidebar.checkbox("Enable Scenario Simulation", value=False)

scenario_overrides = {}
if enable_scenario:
    st.sidebar.subheader("Adjust Macro Variables")
    scenario_overrides['fed_rate'] = st.sidebar.slider("Fed Funds Rate (%)", 0.0, 10.0, 3.63, 0.25)
    scenario_overrides['cpi'] = st.sidebar.slider("CPI Inflation YoY (%)", 0.0, 10.0, 3.35, 0.1)
    scenario_overrides['unemployment'] = st.sidebar.slider("Unemployment Rate (%)", 2.0, 10.0, 4.1, 0.1)
    scenario_overrides['gdp_growth'] = st.sidebar.slider("GDP Growth YoY (%)", -3.0, 6.0, 2.1, 0.1)
    scenario_overrides['yield_spread'] = st.sidebar.slider("10Y-2Y Spread (%)", -2.0, 3.0, 0.33, 0.05)

if st.button("Run Live Scan"):
    with st.spinner("Fetching macro indicators, DXY spot price, and news..."):
        macro_metrics, error = get_macro_data()
        dxy_price, dxy_change = get_dxy_data()
        ff_events = get_forexfactory_usd_events()
        investing_news = get_investing_usd_news()

    if enable_scenario and macro_metrics:
        st.warning("⚠️ **Scenario Mode Active:** Displaying simulated results based on sidebar inputs.")
        macro_metrics.update(scenario_overrides)

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
            elif "BEARISH" in bias_str:
                st.error("• **Primary Trade:** Long EUR/USD or Long Gold (XAU/USD).")
            else:
                st.warning("• **Primary Trade:** Range-trading strategies / Mean-reversion.")

        # Quantitative Statistical & Backtest Engine
        st.divider()
        st.subheader("Quantitative Statistical Modeling Suite")
        
        hist_df, hist_err = get_historical_macro_matrix()
        if hist_df is not None:
            m_tab1, m_tab2, m_tab3, m_tab4, m_tab5 = st.tabs([
                "ARIMA Time-Series", 
                "Binary Logistic Regression", 
                "Discriminant Analysis (LDA)", 
                "PCA Dimensionality",
                "Strategy Backtest Engine"
            ])

            with m_tab1:
                st.markdown("#### 3-Month ARIMA (1,1,1) CPI Projections")
                cpi_forecast, arima_err = run_arima_forecast(hist_df['cpi'])
                if cpi_forecast is not None:
                    st.dataframe(cpi_forecast.to_frame('Projected CPI (%)'))
                else:
                    st.warning(arima_err)

            with m_tab2:
                st.markdown("#### Logistic Regression Directional Classifier")
                logit_res, logit_err = run_logistic_regression(hist_df)
                if logit_res:
                    st.metric("Statistical Probability P(DXY Close UP Next Month)", f"{logit_res['prob_up']:.1f}%")
                    st.dataframe(logit_res['coefficients'])
                else:
                    st.warning(logit_err)

            with m_tab3:
                st.markdown("#### Discriminant Analysis Macro Regime Classification")
                lda_res, lda_err = run_lda_model(hist_df)
                if lda_res:
                    regime_map = {1: "Bullish Regime", 0: "Range-Bound Regime", -1: "Bearish Regime"}
                    st.info(f"**Current LDA Projected Regime:** {regime_map.get(lda_res['regime'], 'Unknown')}")
                    st.bar_chart(lda_res['probabilities'])
                else:
                    st.warning(lda_err)

            with m_tab4:
                st.markdown("#### Principal Component Analysis (PCA)")
                pca_res, pca_err = run_pca_decomposition(hist_df)
                if pca_res:
                    st.write(f"**Total Variance Explained:** {sum(pca_res['explained_variance']):.1f}%")
                    st.dataframe(pca_res['components'])
                else:
                    st.warning(pca_err)

            with m_tab5:
                st.markdown("#### Historical Walk-Forward Strategy Backtest")
                bt_res, bt_err = run_historical_backtest(hist_df)
                if bt_res:
                    col_bt1, col_bt2 = st.columns(2)
                    with col_bt1:
                        st.metric("Out-of-Sample Model Accuracy", f"{bt_res['win_rate']:.1f}%")
                    with col_bt2:
                        st.metric("Total Evaluation Periods", f"{bt_res['total_trades']} Months")
                    st.write("**Recent Out-of-Sample Predictions vs Actual Outcomes:**")
                    st.dataframe(bt_res['results_df'].tail(12))
                else:
                    st.warning(bt_err)

            st.caption(
                "💡 **Model Convergence Note:** The 3-Month Macro Framework Heuristic evaluates fundamental policy gap (Taylor Rule) "
                "over a 90-day horizon, while the Logistic Classifier computes a rolling 30-day statistical probability based on 5-year historical returns."
            )
        else:
            st.warning(f"Could not initialize statistical models: {hist_err}")

    else:
        st.error(error)

    st.divider()

    st.subheader("USD News & Economic Calendar")
    tab1, tab2 = st.tabs(["ForexFactory Calendar", "Investing.com Breaking News"])

    with tab1:
        st.markdown("### Upcoming USD Economic Events")
        for event in ff_events:
            st.markdown(event)

    with tab2:
        st.markdown("### USD & Fed Market Headlines")
        for item in investing_news:
            st.markdown(f"• [{item['title']}]({item['link']}) — *{item['published']}*")
