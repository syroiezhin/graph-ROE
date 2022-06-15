import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import streamlit as st

COINS = set(["1000shibusdt","1000xecusdt","1inchusdt","aaveusdt","adausdt","algousdt","alphausdt","ankrusdt","antusdt","apeusdt",
"api3usdt","arpausdt","arusdt","atausdt","atomusdt","audiousdt","avaxusdt","axsusdt","bakeusdt","balusdt","bandusdt","bchusdt",
"belusdt","blzusdt","bnbusdt","bnxusdt","btcdomusdt","btcusdt","c98usdt","celousdt","celrusdt","chrusdt","chzusdt","compusdt",
"cotiusdt","crvusdt","ctkusdt","ctsiusdt","cvcusdt","darusdt","dashusdt","defiusdt","dentusdt","dgbusdt","dogeusdt","dotusdt",
"duskusdt","dydxusdt","egldusdt","enjusdt","ensusdt","eosusdt","etcusdt","ethusdt","ethusdt","filusdt","flmusdt","flowusdt",
"ftmusdt","fttusdt","galausdt","galusdt","gmtusdt","grtusdt","gtcusdt","hbarusdt","hntusdt","hotusdt","icpusdt","imxusdt",
"iostusdt","iotausdt","iotxusdt","jasmyusdt","kavausdt","klayusdt","kncusdt","ksmusdt","linausdt","linkusdt","litusdt","lptusdt",
"lrcusdt","ltcusdt","manausdt","maskusdt","maticusdt","mkrusdt","mtlusdt","nearusdt","neousdt","nknusdt","oceanusdt","ognusdt","omgusdt",
"oneusdt","ontusdt","opusdt","peopleusdt","qtumusdt","rayusdt","reefusdt","renusdt","rlcusdt","roseusdt","rsrusdt","runeusdt","rvnusdt",
"sandusdt","scusdt","sfpusdt","sklusdt","snxusdt","solusdt","srmusdt","stmxusdt","storjusdt","sushiusdt","sxpusdt","thetausdt","tlmusdt",
"tomousdt","trbusdt","trxusdt","unfiusdt","uniusdt","wavesusdt","woousdt","xemusdt","xlmusdt","xmrusdt","xrpusdt","xtzusdt","yfiusdt",
"zecusdt","zenusdt","zilusdt","zrxusdt"])


def candles(symbol, interval, limit):
    url = 'https://fapi.binance.com/fapi/v1/klines'
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    r = requests.get(url, params=params)
    df = pd.DataFrame(r.json())
    df = df[[0, 1, 2, 3, 4, 5]]
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    df['date'] = df['date'] + pd.Timedelta(hours=3)
    df = df.set_index('date')

    for column in df.columns:
        df[column] = df[column].astype(float)

    df['roe'] = df.apply(lambda x: ((x.high - x.low) / x.low) * 100, axis=1)
    df['prev_open'] = df['open'].shift(1)
    df['roe'] = df.apply(lambda x: -x.roe if x.close < x.prev_open else x.roe, axis=1)
    df['cumroe'] = df['roe'].cumsum()
    return df


def visualize(df):
      
    colors = ['green' if row['open'] - row['close'] >= 0
        else 'red' for index, row in df.iterrows()]


    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                vertical_spacing=0.01,
                row_heights=[0.5, 0.2])


    fig.add_trace(go.Candlestick(x=df.index,
                            open=df['open'], high=df['high'],
                            low=df['low'], close=df['close'], name='candles'))


    fig.add_trace(go.Bar(x=df.index,
                    y=df['volume'],
                    marker_color=colors,
                    name='Volume'),
            row=2, col=1)


    fig.update_layout(
        yaxis_title='Stock Price ($)',
        xaxis_title='Time(utc+3)',
        xaxis_rangeslider_visible=True, template='plotly_dark')

    fig.update_yaxes(title_text="Volume", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)


    f = go.Figure(go.Scatter(x=df.index, y=df['cumroe'], line=dict(
                color='#D7311B', width=3), name='cumroe'))
    # f.update_traces(mode='markers', marker_line_width=2, marker=dict(
    #         size=6,
    #         color=df['cumroe'], 
    #         colorscale='reds', 
    #         showscale=True
    #     ))
    f.update_layout(title='ROE',
                    yaxis_zeroline=False, xaxis_zeroline=False, xaxis_rangeslider_visible=True)
    st.plotly_chart(f, use_container_width=True)



st.set_page_config(
     page_title="Binance Chart",
     layout="wide",
     page_icon="📈",
     initial_sidebar_state="expanded")



with st.sidebar.form(key ='data_options'):
    st.write("Options")
    coin = st.selectbox('coin', COINS)
    interval = st.selectbox("interval", ('1m', '5m', '1d', '1w', '1M'))
    limit = st.text_input('limit')
    submitted = st.form_submit_button("Submit")


if submitted:
    df = candles(coin, interval, int(limit))
    visualize(df)