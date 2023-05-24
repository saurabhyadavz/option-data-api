from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from frontend.utils import utils
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.sidebar.title('Options Data')
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")
if start_date > end_date:
    st.error("End date should be less than start_date")
elif (end_date - start_date).days > 60:
    st.error("Difference between start date and date should be less than 2 months")
else:
    index = st.sidebar.selectbox("Select Index", ["BANKNIFTY", "NIFTY"])
    if start_date and end_date:
        all_expiry_dates_dict = utils.get_expiry_between_dates(index, start_date, end_date)
        all_expiry_dates = list(all_expiry_dates_dict.keys())
        all_expiry_dates = sorted(all_expiry_dates)
        expiry_date = None
        if all_expiry_dates:
            expiry_date = st.sidebar.selectbox("Select Expiry", all_expiry_dates)
        strike_range = None
        if expiry_date:
            with st.spinner('Loading strikes'):
                expiry_format = utils.get_value(all_expiry_dates_dict, expiry_date)
                strike_range = utils.get_unique_options_strike(index, expiry_format, start_date, end_date)
        if strike_range:
            strike = st.sidebar.selectbox("Option Strike", strike_range)
            option_type = st.sidebar.selectbox("Option Type", ["CE", "PE"])
            option_contract = utils.generate_options_contract(index, expiry_date, strike, option_type)
            if option_contract:
                contract_df = utils.get_options_df(option_contract, start_date, end_date)
                if contract_df is not None:
                    timeframe = st.sidebar.selectbox("Time Frame", ["1min", "5min",
                                                                    "10min", "15min",
                                                                    "30min", "60min"])
                    resampled_df = utils.resample_ohlc_df(contract_df, timeframe)
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=resampled_df.index,
                        open=resampled_df["open"],
                        high=resampled_df["high"],
                        low=resampled_df["low"],
                        close=resampled_df["close"]
                    ))
                    fig.update_layout(
                        title=option_contract,
                        xaxis=dict(
                            rangeslider_visible=False,
                            type="category"
                        )
                    )
                    st.plotly_chart(fig, theme=None, use_container_width=True)
                else:
                    st.info(f"Data not present for {option_contract}")
        else:
            st.error(f"{start_date} is NSE Holiday or data not present")

utils.dump_expiry()
