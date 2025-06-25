import streamlit as st
import yfinance as yf
import plotly.express as px


def run():
    if st.button("↩︎  Go to Volatility Surface"):
        st.session_state.page = "Volatility Surface"
        st.experimental_rerun()

    st.title("Volatility Smile")

    ticker_list = ["SPY", "QQQ", "IWM", "^SPX"]
    selected_ticker = st.selectbox("Select Ticker", ticker_list)

    ticker = yf.Ticker(selected_ticker)

    current_price = ticker.info['regularMarketPrice']

    expirations = ticker.options

    selected_expiry = st.selectbox("Select Expiration", expirations)

    option_chain = ticker.option_chain(selected_expiry)

    calls = option_chain.calls[['strike', 'impliedVolatility']].copy()
    puts = option_chain.puts[['strike', 'impliedVolatility']].copy()
    calls.dropna(inplace=True)
    puts.dropna(inplace=True)

    use_same_range = st.checkbox("Use same strike range for calls and puts?", value=False)

    calls_min, calls_max = calls['strike'].min(), calls['strike'].max()
    puts_min, puts_max = puts['strike'].min(), puts['strike'].max()

    if use_same_range:
        min_strike = float(min(calls_min, puts_min))
        max_strike = float(max(calls_max, puts_max))

        strike_range = st.slider("Strike Price Range", min_value=min_strike, max_value=max_strike,
                                 value=(min_strike, max_strike), step=1.0)

        calls_filtered = calls[(calls['strike'] >= strike_range[0]) & (calls['strike'] <= strike_range[1])]
        puts_filtered = puts[(puts['strike'] >= strike_range[0]) & (puts['strike'] <= strike_range[1])]
    else:
        call_range = st.slider(
            "Strike Price Range for Calls",
            min_value=float(calls_min),
            max_value=float(calls_max),
            value=(float(calls_min), float(calls_max)),
            step=1.0
        )
        put_range = st.slider(
            "Strike Price Range for Puts",
            min_value=float(puts_min),
            max_value=float(puts_max),
            value=(float(puts_min), float(puts_max)),
            step=1.0
        )
        calls_filtered = calls[(calls['strike'] >= call_range[0]) & (calls['strike'] <= call_range[1])]
        puts_filtered = puts[(puts['strike'] >= put_range[0]) & (puts['strike'] <= put_range[1])]

    st.subheader("Calls")

    fig = px.line(
        calls_filtered,
        x="strike",
        y="impliedVolatility",
        title=f"{selected_ticker} Calls ({selected_expiry})",
        labels={"strike": "Strike Price", "impliedVolatility": "Implied Volatility"}
    )
    fig.add_vline(x=current_price, line_dash="dash", line_color="red",
                  annotation_text=f"Current Price: ${current_price:.2f}", annotation_position="top")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show raw option data"):
        st.dataframe(calls_filtered)

    st.subheader("Puts")

    fig = px.line(
        puts_filtered,
        x="strike",
        y="impliedVolatility",
        title=f"{selected_ticker} Puts ({selected_expiry})",
        labels={"strike": "Strike Price", "impliedVolatility": "Implied Volatility"}
    )
    fig.add_vline(x=current_price, line_dash="dash", line_color="red",
                  annotation_text=f"Current Price: ${current_price:.2f}", annotation_position="top")
    st.plotly_chart(fig, use_container_width=True)

    # Optional: display the table
    with st.expander("Show raw option data"):
        st.dataframe(puts_filtered)