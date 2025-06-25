import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

def show_sidebar():
    open_sidebar_script = """
    <script>
    const sidebarToggle = window.parent.document.querySelector('[aria-label="Toggle sidebar"]');
    if (sidebarToggle) {
        const isExpanded = window.parent.document.querySelector('nav[aria-label="Sidebar"]').getAttribute('aria-expanded');
        if (isExpanded === "false") {
            sidebarToggle.click();
        }
    }
    </script>
    """
    st.components.v1.html(open_sidebar_script)

def run():
    show_sidebar()

    st.title("Volatility Surface")

    ticker_list = ["SPY", "QQQ", "IWM", "^SPX"]
    selected_ticker = st.selectbox("Select Ticker", ticker_list)

    ticker = yf.Ticker(selected_ticker)

    current_price = ticker.info['regularMarketPrice']

    expirations = pd.to_datetime(ticker.options)

    # Get default date range
    min_date = expirations.min()

    exp_sorted = sorted(expirations.to_list())

    cutoff_index = 0
    for i in range(1, len(exp_sorted)):
        diff = (exp_sorted[i] - exp_sorted[i - 1]).days
        if diff > 4:
            break
        cutoff_index = i

    default_end_date = exp_sorted[cutoff_index]

    expirations_str = [d.strftime("%Y-%m-%d") for d in expirations]

    start_date_str = st.selectbox("Start expiration date", expirations_str, index=0)
    end_date_str = st.selectbox("End expiration date", expirations_str, index=expirations.get_loc(default_end_date))

    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)

    selected_expirations = [d for d in expirations if start_date <= d <= end_date]

    option_type = st.radio("Select option type", ["Calls", "Puts"])
    x_axis_type = st.radio("X-axis scale", ["Strike Price", "Moneyness"])

    all_data = []

    for expiry in selected_expirations:
        expiry_str = expiry.strftime("%Y-%m-%d")
        option_chain = ticker.option_chain(expiry_str)
        df = option_chain.calls if option_type == "Calls" else option_chain.puts
        df = df[['strike', 'impliedVolatility']].dropna()
        df['expiry'] = pd.to_datetime(expiry)
        all_data.append(df)

    surface_df = pd.concat(all_data)
    surface_df['days_to_expiry'] = (surface_df['expiry'] - pd.Timestamp.today()).dt.days

    surface_df['moneyness'] = surface_df['strike'] / current_price

    if x_axis_type == "Moneyness":
        surface_df['x_value'] = surface_df['moneyness']
        surface_df = surface_df.sort_values("x_value")
        x_label = "Moneyness"
    else:
        surface_df['x_value'] = surface_df['strike']
        x_label = "Strike Price"

    x_min, x_max = float(surface_df['x_value'].min()), float(surface_df['x_value'].max())

    user_range = st.slider(
        f"Select {x_label} range",
        min_value=round(x_min, 2),
        max_value=round(x_max, 2),
        value=(round(x_min, 2), round(x_max, 2))
    )

    surface_df = surface_df[(surface_df['x_value'] >= user_range[0]) & (surface_df['x_value'] <= user_range[1])]

    x = surface_df['x_value'].values
    y = surface_df['days_to_expiry'].values
    z = surface_df['impliedVolatility'].values

    xi = np.linspace(x.min(), x.max(), 50)
    yi = np.linspace(y.min(), y.max(), 50)
    xi, yi = np.meshgrid(xi, yi)

    zi = griddata((x, y), z, (xi, yi), method='cubic')

    st.subheader(f"{selected_ticker} {option_type} Volatility Surface ({x_axis_type})")

    fig = go.Figure(data=[go.Surface(
        x=xi,
        y=yi,
        z=zi,
        colorscale='Viridis',
        colorbar=dict(title="Implied Volatility"),
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title=x_label,
            yaxis_title='Days to Expiry',
            zaxis_title='Implied Volatility',
        ),
        margin=dict(l=10, r=10, b=10, t=40),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show raw data"):
        st.dataframe(surface_df)