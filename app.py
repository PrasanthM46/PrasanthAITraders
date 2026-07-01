import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import traceback
from strategy import load_data, compute_indicators, latest_signal
from alert_utils import load_latest_alert

st.set_page_config(page_title="Trading Signal Dashboard", page_icon="📈", layout="wide")

st.title("Olymp Trade Fixed-Time Signal Dashboard")
st.markdown(
    "This dashboard loads recent market data, calculates a simple EMA+RSI signal, and highlights CALL/PUT setup alerts."
)

with st.sidebar:
    st.header("Dashboard settings")
    ticker = st.text_input("Ticker", "EURUSD=X")
    interval = st.selectbox("Interval", ["1m", "2m", "5m", "15m"], index=0)
    period = st.selectbox("History period", ["1d", "2d", "5d", "7d"], index=1)
    show_data = st.checkbox("Show raw data table", value=False)
    show_signals = st.checkbox("Highlight signal history", value=True)
    enable_sound = st.checkbox("Play alert sound for BUY/SELL", value=False)

try:
    with st.spinner(f"Loading {ticker} data..."):
        df = load_data(ticker, period=period, interval=interval)
        df = compute_indicators(df)

    if df.empty or "Close" not in df.columns:
        st.error("No data was returned or the loaded data is missing the Close price. Check the ticker symbol, interval, or your internet connection.")
    else:
        signal = latest_signal(df)
        latest = df.iloc[-1]
        signal_label = "BUY" if signal == "CALL" else "SELL" if signal == "PUT" else "HOLD"
        ha_status = "Bullish" if latest.HA_Bull else "Bearish" if latest.HA_Bear else "Neutral"

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Price, EMA and Heikin Ashi")
            st.line_chart(df[["Close", "EMA50", "HA_Close"]].rename(columns={"Close": "Close Price", "HA_Close": "HA Close"}))
        with col2:
            st.subheader("Live trade signal")
            st.metric("Ticker", ticker)
            st.metric("Interval", interval)
            st.metric("Trade action", signal_label)
            st.metric("Last close", f"{latest.Close:.5f}")
            st.metric("RSI 14", f"{latest.RSI:.1f}")
            st.metric("HA candle", ha_status)

        banner_color = "#22c55e" if signal_label == "BUY" else "#ef4444" if signal_label == "SELL" else "#fbbf24"
        banner_icon = "🚀" if signal_label == "BUY" else "⚠️" if signal_label == "SELL" else "⏳"
        banner_text = (
            "BUY now" if signal_label == "BUY" else "SELL now" if signal_label == "SELL" else "HOLD / WAIT"
        )
        banner_message = (
            "Price is above EMA50 and RSI is low. Look for a bullish 1m candle to enter." if signal_label == "BUY"
            else "Price is below EMA50 and RSI is high. Look for a bearish 1m candle to enter." if signal_label == "SELL"
            else "No clear entry signal yet. Wait for the price to move clearly above or below EMA50."
        )

        st.markdown(
            f"<div style='padding: 28px; border-radius: 14px; background: {banner_color}; color: #ffffff; font-size: 24px; font-weight: 800;'>"
            f"<span style='font-size: 32px; margin-right: 12px;'>{banner_icon}</span>"
            f"<span>{banner_text}</span><br>"
            f"<span style='font-size: 16px; font-weight: 500; opacity: 0.95;'>{banner_message}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if enable_sound and signal_label in ["BUY", "SELL"]:
            components.html(
                "<audio autoplay><source src='https://actions.google.com/sounds/v1/alarms/beep_short.ogg' type='audio/ogg'></audio>"
            )

        alert = load_latest_alert()
        if alert is not None:
            st.markdown("---")
            st.subheader("Latest TradingView alert")
            st.write(alert)

        st.markdown("---")
        st.subheader("Indicator details")
        st.write(
            "This example uses a 50-period EMA and a 14-period RSI. CALL is suggested when price is above EMA and RSI < 35. PUT is suggested when price is below EMA and RSI > 65."
        )

        if show_signals:
            signal_df = df.loc[df["Signal"] != "NONE", ["Close", "EMA50", "RSI", "HA_Close", "Signal"]].copy()
            if not signal_df.empty:
                st.write("### Recent trade signals")
                st.dataframe(signal_df.tail(20))
            else:
                st.write("No CALL/PUT signals found in the loaded history.")

        if show_data:
            st.markdown("### Raw market data")
            st.dataframe(df.tail(50))

except Exception as exc:
    st.error(f"Unable to load dashboard: {exc}")
    st.text(traceback.format_exc())

# Auto-refresh is handled by st_autorefresh above.
