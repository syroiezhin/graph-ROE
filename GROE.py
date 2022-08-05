from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import requests

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

    df['roe'] = df.apply(lambda x: ((x.close - x.open) / x.open) * 100, axis=1) 
    df['cumroe'] = df['roe'].cumsum()
    df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['EMA7'] = df['close'].ewm(span=7, adjust=False).mean()


    df['roe_low'] = df.apply(lambda x:  
        x.cumroe - (((x.close - x.low) / x.open) * 100) if x.close < x.open else x.cumroe - (((x.open - x.low) / x.open) * 100), axis=1)
    df['roe_high'] = df.apply(lambda x: 
        x.cumroe + (((x.high - x.open) / x.open) * 100) if x.close < x.open else x.cumroe + (((x.high - x.close) / x.open) * 100), axis=1)
    return df

def visualize(df, coin, first_chart):
      
    colors = ['red' if row['open'] - row['close'] >= 0
        else 'green' for index, row in df.iterrows()]


    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                vertical_spacing=0.03, 
                row_heights=[0.40, 0.20, 0.40])  


    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name=coin))
    fig.add_trace(go.Scatter(x=df.index, y=df['cumroe'], line=dict(color='#09b683', width=3), name='ROE (%)'), row=3, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], opacity=0.5, marker_color=colors, name='Volume'), row=2, col=1)
    fig.update_yaxes(title_text="ROE (%)", row=3, col=1)


    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(
                   color='#49B9E3'), name='EMA50'), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(
                   color='#81E349'), name='EMA20'), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['EMA7'], line=dict(
                   color='#ffa226'), name='EMA7'), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['roe_low'], line=dict(
                    color='#ace5ee'), name='low'), row=3, col=1)\

    fig.add_trace(go.Scatter(x=df.index, y=df['roe_high'], line=dict(
                    color='#aa0905'), name='high'), row=3, col=1)

    fig.update_layout(
        height=750,
        yaxis_title='Stock Price ($)',
        xaxis_rangeslider_visible=True, 
        xaxis_rangeslider_thickness=0.01,
        xaxis_rangeslider_bgcolor='#902416',
        template='plotly_dark',
        legend=dict( orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1 ) 
        )

    if first_chart:
        placeholder.plotly_chart(fig, use_container_width=True)

    else:
        st.plotly_chart(fig, use_container_width=True)

st.set_page_config(
     page_title="Binance Chart",
     layout="wide",
     page_icon="📈",
     initial_sidebar_state="expanded")

with st.sidebar.form(key ='coin_chart_options'):
    st.write("Coin chart")
    coin = st.selectbox('coin', COINS)
    interval = st.selectbox("interval", ('1m', '5m', '15m', '1h', '1d', '1w', '1M'))
    limit = st.selectbox("limit", ('60', '300', '600', '1200', '1500')) 
    coin_chart_button = st.form_submit_button("Submit")
    
placeholder = st.empty()

df = candles(coin, interval, int(limit))
visualize(df, coin, True)

if coin_chart_button:
    with placeholder.container():
        df = candles(coin, interval, int(limit))
        visualize(df, coin, False)

with st.sidebar.form(key ='top_coins_charts'):
    st.write("Top growing coins")
    interval = st.selectbox("interval", ('1m', '5m', '15m', '1h', '1d', '1w', '1M'))
    limit = st.selectbox("limit", ('60', '300', '600', '1200', '1500')) 
    top_coins_button = st.form_submit_button("Submit")

if top_coins_button:

    d = {'coin':[], 'value':[]}

    with placeholder.container():
        with st.spinner('Calculation...'):

            for pos, coin in enumerate(COINS):

                df = candles(f'{coin}', '1d', 180)
                
                coin_min = df['close'].min()

                coin_max = df['close'].max()

                coin_now = df['close'].iloc[-1]

                d['value'].append(round(((coin_now - coin_min) / (coin_max - coin_min)) * 100, 2))

                d['coin'].append(coin)

            

        df = pd.DataFrame(d)

        top_coins = df.sort_values(ascending=False, by='value').head(3)['coin'].to_list()

        for coin in top_coins:
            st.markdown(f'**{coin}**')
            df = candles(coin, interval, int(limit))
            visualize(df, coin, False)