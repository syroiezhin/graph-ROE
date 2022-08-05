# share.streamlit.io
from streamlit import set_page_config, spinner, markdown, columns, text_input, empty, sidebar, selectbox, form_submit_button, plotly_chart, write
from plotly.graph_objects import Candlestick, Scatter, Bar
from pandas import DataFrame, Timedelta, to_datetime
from tradingview_ta import TA_Handler, Interval
from plotly.subplots import make_subplots
from time import strftime, localtime
from requests import get

# conda install -c plotly plotly
# conda install streamlit
# pip install tradingview_ta
# pip install requests
# pip install pandas
# pip install time

def signal(symbol):
    output = TA_Handler( symbol=symbol, screener = 'crypto', exchange = 'BINANCE', interval = Interval.INTERVAL_15_MINUTES).get_analysis() 
    now = str(strftime("%H:%M:%S",  localtime()))
    result = f"{output.summary['RECOMMENDATION']} {symbol.upper()} : B {round((100/26)*output.summary['BUY'], 2)} % / N {round((100/26)*output.summary['NEUTRAL'], 2)} % / S {round((100/26)*output.summary['SELL'], 2)} %"
    print(f"{now} {symbol} | {result}")
    return result

def candles(symbol, interval, limit, leverage):
    url = 'https://fapi.binance.com/fapi/v1/klines'
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    r = get(url, params=params)
    df = DataFrame(r.json())
    df = df[[0, 1, 2, 3, 4, 5]]
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    df['date'] = to_datetime(df['date'], unit='ms')
    df['date'] = df['date'] + Timedelta(hours=3)
    df = df.set_index('date')

    for column in df.columns: df[column] = df[column].astype(float)
    
    df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['EMA7'] =  df['close'].ewm(span=7,  adjust=False).mean()
    
    df['cumroe'] = df.apply(lambda x: (((x.close - x.open) / x.open) * 100), axis=1).cumsum()
    df['roe_low']  = df.apply(lambda x: leverage*(x.cumroe - (((x.close - x.low) / x.open) * 100)) if x.close < x.open else leverage*(x.cumroe - (((x.open - x.low) / x.open) * 100)), axis=1)
    df['roe_high'] = df.apply(lambda x: leverage*(x.cumroe + (((x.high - x.open) / x.open) * 100)) if x.close < x.open else leverage*(x.cumroe + (((x.high - x.close) / x.open) * 100)), axis=1)
    df['roe'] = leverage*df['cumroe']
    return df

def visualize(df, coin, boolean_key, limit, interval, placeholder):
      
    colors = ['red' if row['open'] - row['close'] >= 0
        else 'green' for index, row in df.iterrows()]

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.40, 0.20, 0.40])  

    fig.add_trace(Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name=f'<b>{coin}</b>'))
    fig.update_yaxes(title_text="Volume", titlefont=dict( color="#1f77b4" ), tickfont=dict( color="#1f77b4" ), anchor="x", overlaying="y", side="right")
    fig.add_trace(Bar(x=df.index, y=df['volume'], opacity=0.5, marker_color=colors, name='Volume'), row=2, col=1)
    
    fig.add_trace(Scatter(x=df.index, y=df['roe_high'], line=dict(color='#aa0905'), name='High'), row=3, col=1)
    fig.add_trace(Scatter(x=df.index, y=df['roe'],      line=dict(color='#09b683'), name='ROE (%)'), row=3, col=1)
    fig.add_trace(Scatter(x=df.index, y=df['roe_low'],  line=dict(color='#ace5ee'), name='Low'), row=3, col=1)
    fig.update_yaxes(title_text="ROE (%)", titlefont=dict( color="#1f77b4" ), tickfont=dict( color="#1f77b4" ), anchor="x", overlaying="y", side="right")

    fig.add_trace(Scatter(x=df.index, y=df['EMA50'], line=dict(color='#49B9E3'), name='EMA50'), row=1, col=1)
    fig.add_trace(Scatter(x=df.index, y=df['EMA20'], line=dict(color='#81E349'), name='EMA20'), row=1, col=1)
    fig.add_trace(Scatter(x=df.index, y=df['EMA7'], line=dict(color='#ffa226'), name='EMA7'), row=1, col=1)

    candle = {'1m':"minute", '5m':"minute", '15m':"minute", '1h':"hour", '1d':"day"}
    gauge = int(''.join(filter(lambda x: x not in set(['m', 'h', 'd']), interval)))

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                font_color='black',
                activecolor='red',
                bgcolor='green',
                buttons=list([
                    dict(count=int(gauge)*int(limit)/100, label="1%",   step=candle[interval], stepmode="backward"),
                    dict(count=int(gauge)*int(limit)/20,  label="5%",   step=candle[interval], stepmode="backward"),
                    dict(count=int(gauge)*int(limit)/10,  label="10%",  step=candle[interval], stepmode="backward"),
                    dict(count=int(gauge)*int(limit)/4,   label="25%",  step=candle[interval], stepmode="backward"),
                    dict(count=int(gauge)*int(limit)/2,   label="50%",  step=candle[interval], stepmode="backward"),
                    dict(count=int(gauge)*int(limit),     label="100%", step=candle[interval], stepmode="backward"),
                    dict(step="all", label="practical")
                ])
            ),
            rangeslider=dict( visible=True, thickness=0.01, bgcolor='#902416' ),
            type="date"
        ),
        height=750,
        template='plotly_dark',
        legend=dict( orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1 ),
        yaxis=dict( title_text='Stock Price ($)', titlefont=dict( color="#1f77b4" ), tickfont=dict( color="#1f77b4" ), anchor="x", overlaying="y", side="right" )
    ) 
    fig.update_layout(template='plotly_dark', xaxis_rangeselector_font_color='black', xaxis_rangeselector_activecolor='red', xaxis_rangeselector_bgcolor='green' )

    if boolean_key: placeholder.plotly_chart(fig, use_container_width=True)
    else: plotly_chart(fig, use_container_width=True)

def option():
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

    set_page_config(page_title="Binance Chart", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

    with sidebar.form(key ='options'):

        # write("Options")
        leverage = int(selectbox("Futures", ('1', '5', '10', '20', '40', '80')))
        interval = selectbox("Сandles", ('1d', '1h', '15m', '5m', '1m'))
        limit = selectbox("Interval", ('1440', '720', '480', '240', '60', '24')) 

        c1, c2 = columns(2)
        with c1: 
            coin = selectbox('Choose Coin', COINS)
            coin_chart_button = form_submit_button("RUN") # "show the graph of the selected coin"
        with c2: 
            number_of_graphs = text_input('Show Top Coins', "3")
            top_coins_button = form_submit_button("SHOW") # "show a graph of the top {number_of_graphs} coins by growth"

    placeholder = empty()
    df = candles(coin, interval, int(limit), leverage)
    visualize(df, coin, True, limit, interval, placeholder)

    if coin_chart_button:
        with placeholder.container():
            markdown(f'**{signal(coin)}**')
            df = candles(coin, interval, int(limit), leverage)
            visualize(df, coin, False, limit, interval, placeholder)

    if top_coins_button:
        d = {'coin':[], 'value':[]}
        with placeholder.container():
            with spinner('Calculation...'):
                for pos, coin in enumerate(COINS):
                    df = candles(coin, interval, int(limit), leverage)
                    coin_min = df['close'].min()
                    coin_max = df['close'].max()
                    coin_now = df['close'].iloc[-1]
                    d['value'].append(round(((coin_now - coin_min) / (coin_max - coin_min)) * 100, 2))
                    d['coin'].append(coin)

            df = DataFrame(d)
            if number_of_graphs == "" or int(number_of_graphs) > 10: number_of_graphs = "3"
            top_coins = df.sort_values(ascending=False, by='value').head(int(number_of_graphs))['coin'].to_list()
            for coin in top_coins:
                df = candles(coin, interval, int(limit), leverage)
                visualize(df, coin, False, limit, interval, placeholder)

if __name__ == "__main__": option()