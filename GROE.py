# share.streamlit.io
from streamlit import set_page_config, experimental_rerun, info, progress, form, checkbox, columns, empty, selectbox, form_submit_button, plotly_chart, multiselect, session_state
from plotly.graph_objects import Candlestick, Scatter, Bar
from pandas import DataFrame, Timedelta, to_datetime
from tradingview_ta import TA_Handler, Interval
from plotly.subplots import make_subplots
from requests import get
from time import sleep

# conda install -c plotly plotly
# conda install streamlit
# pip install tradingview_ta
# pip install requests
# pip install pandas
# pip install time

def signal(symbol):
    output = TA_Handler( symbol=symbol, screener = 'crypto', exchange = 'BINANCE', interval = Interval.INTERVAL_15_MINUTES).get_analysis() 
    result = f"{output.summary['RECOMMENDATION']} {symbol.upper()} : B {round((100/26)*output.summary['BUY'], 2)} % / N {round((100/26)*output.summary['NEUTRAL'], 2)} % / S {round((100/26)*output.summary['SELL'], 2)} %"
    # now = str(strftime("%H:%M:%S",  localtime()))
    # print(f"{now} {symbol} | {result}")
    return result

def candles(symbol, interval, limit, leverage, key_ema, key_roe):

    df = DataFrame(get('https://fapi.binance.com/fapi/v1/klines', params={'symbol': symbol, 'interval': interval, 'limit': limit}).json())
    df = df[[0, 1, 2, 3, 4, 5]]
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    df['date'] = to_datetime(df['date'], unit='ms')
    df['date'] = df['date'] + Timedelta(hours=3)
    df = df.set_index('date')

    for column in df.columns: df[column] = df[column].astype(float)
    
    if key_ema == True:
        df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['EMA7'] =  df['close'].ewm(span=7,  adjust=False).mean()
    
    if key_roe == True:
        df['cumroe'] = df.apply(lambda x: (((x.close - x.open) / x.open) * 100), axis=1).cumsum()
        df['roe_low']  = df.apply(lambda x: leverage*(x.cumroe - (((x.close - x.low) / x.open) * 100)) if x.close < x.open else leverage*(x.cumroe - (((x.open - x.low) / x.open) * 100)), axis=1)
        df['roe_high'] = df.apply(lambda x: leverage*(x.cumroe + (((x.high - x.open) / x.open) * 100)) if x.close < x.open else leverage*(x.cumroe + (((x.high - x.close) / x.open) * 100)), axis=1)
        df['roe'] = leverage*df['cumroe']

    return df

def visualize(df, coin, limit, interval, key_ema, key_roe, key_vol, key_price, key_x, infinity):

    if   sum([key_price,key_vol,key_roe]) == 2:
        if key_x == True:
            if     key_roe == False: heights_row = [0.8,  0.05, 0.15, 0  ]
            elif   key_vol == False: heights_row = [0.48, 0.04, 0,   0.48]
            elif key_price == False: heights_row = [0,    0,    0.2, 0.8 ]
        else:
            if     key_roe == False: heights_row = [0.8, 0, 0.2, 0  ]
            elif   key_vol == False: heights_row = [0.5, 0, 0,   0.5]
            elif key_price == False: heights_row = [0,   0, 0.2, 0.8]

    elif sum([key_price,key_vol,key_roe]) == 1:
        if key_x == True:
            if   key_roe == True:    heights_row = [0,    0,    0, 1 ]
            elif key_vol == True:    heights_row = [0,    0,    1, 0 ]
            elif key_price == True:  heights_row = [0.95, 0.05, 0, 0 ]
        else:
            if   key_roe == True:    heights_row = [0, 0, 0, 1]
            elif key_vol == True:    heights_row = [0, 0, 1, 0]
            elif key_price == True:  heights_row = [1, 0, 0, 0]

    else :                       
        if key_x == True: heights_row = [0.40, 0.05, 0.15, 0.40]
        else:             heights_row = [0.40, 0,    0.2,  0.40]

    fig = make_subplots(rows=4, cols=1, row_heights=heights_row, shared_xaxes=True, vertical_spacing=0.02)

    if key_price == True: 
        fig.add_trace(Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name=f'<b>{coin}</b>'), row= 1, col=1)
        if key_ema == True:
            fig.add_trace(Scatter(x=df.index, y=df['EMA50'], line=dict(color='#49B9E3'), name='EMA50'), row=1, col=1)
            fig.add_trace(Scatter(x=df.index, y=df['EMA20'], line=dict(color='#81E349'), name='EMA20'), row=1, col=1)
            fig.add_trace(Scatter(x=df.index, y=df['EMA7'],  line=dict(color='#ffa226'), name='EMA7'),  row=1, col=1)

    if key_vol == True:
        fig.add_trace(Bar(x=df.index, y=df['volume'], opacity=0.5, marker_color=['red' if row['open'] - row['close'] >= 0 else 'green' for index, row in df.iterrows()], name='Volume'), row=3, col=1)
        fig.update_yaxes(title_text="Volume", titlefont=dict( color="#1f77b4" ), tickfont=dict( color="#1f77b4" ), anchor="x", overlaying="y", side="right", row= 3, col=1)
        
    if key_roe == True:
        fig.add_trace(Scatter(x=df.index, y=df['roe_high'], line=dict(color='#aa0905'), name='High'),    row=4, col=1)
        fig.add_trace(Scatter(x=df.index, y=df['roe'],      line=dict(color='#09b683'), name='ROE (%)'), row=4, col=1)
        fig.add_trace(Scatter(x=df.index, y=df['roe_low'],  line=dict(color='#ace5ee'), name='Low'),     row=4, col=1)
        fig.update_yaxes(title_text="ROE (%)", titlefont=dict( color="#1f77b4" ), tickfont=dict( color="#1f77b4" ), anchor="x", overlaying="y", side="right", row= 4, col=1)

    candle = {'1m':"minute", '5m':"minute", '15m':"minute", '1h':"hour", '1d':"day"}
    gauge = int(''.join(filter(lambda x: x not in set(['m', 'h', 'd']), interval)))

    if key_x == True: fig.update_layout( xaxis=dict( rangeslider=dict( visible=True, thickness=0.05 ) ) )
    else: fig.update_layout( xaxis=dict( rangeslider=dict( visible=False ) ) )

    if infinity == True: fig.update_layout(showlegend=False)
    else: fig.update_layout( legend=dict( orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1 ), xaxis=dict( rangeselector=dict( font_color='white', activecolor='red', bgcolor='green', buttons=list([ dict(count=int(gauge)*int(limit)/100, label="1%",   step=candle[interval], stepmode="backward"), dict(count=int(gauge)*int(limit)/20,  label="5%",   step=candle[interval], stepmode="backward"), dict(count=int(gauge)*int(limit)/10,  label="10%",  step=candle[interval], stepmode="backward"), dict(count=int(gauge)*int(limit)/4,   label="25%",  step=candle[interval], stepmode="backward"), dict(count=int(gauge)*int(limit)/2,   label="50%",  step=candle[interval], stepmode="backward"), dict(count=int(gauge)*int(limit),     label="100%", step=candle[interval], stepmode="backward"), dict(step="all", label="practical") ]) ), type="date" ) )
    
    fig.update_layout( title = signal(coin), template='plotly_dark', height=800, yaxis=dict( title_text='Stock Price ($)', titlefont=dict( color="#1f77b4" ), tickfont=dict( color="#1f77b4" ), anchor="x", overlaying="y", side="right" ) )
    plotly_chart(fig, use_container_width=True)

def draw_graph(COINS, leverage, limit, interval, key_ema, key_roe, key_vol, key_price, loading, key_x, infinity):

    if loading == True: bar = progress(prgrss := 0.0)
    for coin in COINS:
        if loading == True: bar.progress( prgrss := round(prgrss + 0.2/len(COINS),4) )  # ~20%
        df = candles(coin, interval, limit, leverage, key_ema, key_roe)
        if loading == True: bar.progress( prgrss := round(prgrss + 0.4/len(COINS),4) )  # ~60%
        visualize(df, coin, limit, interval, key_ema, key_roe, key_vol, key_price, key_x, infinity)
        if loading == True: bar.progress( prgrss := round(prgrss + 0.4/len(COINS),4) )  # ~99%
    if loading == True: bar.progress( 1.0 )                                             # 100%

def top_coins(COINS, leverage, limit, interval, key_ema, key_roe):
    d = {'coin':[], 'value':[]}
    for pos, coin in enumerate(COINS):
        df = candles(coin, interval, limit, leverage, key_ema, key_roe)
        d['value'].append(round(((df['close'].iloc[-1] - (coin_min := df['close'].min())) / (df['close'].max() - coin_min)) * 100, 2))
        d['coin'].append(coin)
    return DataFrame(d).sort_values(ascending=False, by='value')['coin'].to_list()

def database(save_in, content):
    data = open('coins.txt', 'r').readlines()
    data = [''.join(data[0:save_in]),content,''.join(data[(save_in+1):sum(1 for line in data)])]
    open('coins.txt', 'w').writelines(data)

def save_dropdown(list, leading):
    list.remove(leading)
    list.insert(0, leading)
    return list

def update(placeholder, infinity, selected_coins, leverage, limit, interval, key_ema, key_roe, key_vol, key_price, loading, key_x):  

    if   (infinity == False): 
        with placeholder.container(): draw_graph(selected_coins, leverage, limit, interval, key_ema, key_roe, key_vol, key_price, loading, key_x, infinity)
    else: # True
        while len(selected_coins) <3:
            with placeholder.container():
                draw_graph(selected_coins, leverage, limit, interval, key_ema, key_roe, key_vol, key_price, loading, key_x, infinity)
                sleep(1)#second
        if   len(selected_coins) >2:
            with placeholder.container(): draw_graph(selected_coins, leverage, limit, interval, key_ema, key_roe, key_vol, key_price, loading, key_x, infinity)

def option(): 
    
    set_page_config(page_title="Binance Chart", layout="wide", page_icon="📈", initial_sidebar_state="expanded")
    
    with form(key ='options'):

        scan = open('coins.txt', 'r').readlines()

        candles, interspace, futures, select = columns([1,1,1,9])
        with candles: interval = selectbox("Сandles", save_dropdown(['1d', '1h', '15m', '5m', '1m'], scan[0].replace('\n', '')), key="Сandles", help="candle chart timeframe")
        with interspace: limit = selectbox("Interval", save_dropdown([1440, 720, 480, 240, 96, 60, 24], int(scan[1].replace('\n', ''))), key="Interval", help="number of recent candles on the chart")
        with futures: leverage = selectbox("Futures", save_dropdown([1, 5, 10, 20, 40, 80], int(scan[2].replace('\n', ''))), key="Futures", help="choose a leverage if you are going to evaluate risks on the ROE chart")
        with select: selected_coins = multiselect( 'Choose Coin', scan[5].split(), scan[4].split() , key='Multiselect', help="select the currency you are interested in or use the \"Recommend\" function to sort the drop-down list in the most promising order")

        duff, load, control, recommend, x, price, vol, roe, ema, live, click, duff = columns([2,7,7,9,6,6,7,5,5,5,5,2])
        with load: loading = checkbox("Loading", key='Loading', value=False, help="would you like to watch the loading track?")
        with control: setting = checkbox("Backend", key='Backend', value=False, help="click to view variable storage")
        with recommend: choice = checkbox("Recommend", key='Recommend', value=eval(scan[3].replace('\n', '')), help="changes the sequence of coin names in the dropdown list")
        with x: key_x = checkbox("Slider", key='Slider', value=False, help="x-axis range slider")
        with price: key_price = checkbox("Price", key='Price', value=True, help="stock price")
        with vol: key_vol = checkbox("Volune", key='Volune', value=True, help="volume indicator")
        with roe: key_roe = checkbox("ROE", key='ROE', value=True, help="return on equity")
        with ema: key_ema = checkbox("EMA", key='EMA', value=False, help="exponential moving average")
        with live: infinity = checkbox("Live", key='Live', value=False, help="chart update every second (no more than 2 charts at the same time)")
        with click: use = form_submit_button("USE", help="click to confirm changes")

        if setting == True: session_state # to view the status of variables with key
    
        if choice:
            if eval(scan[3].replace('\n', '')) == False:
                database(3, f"{choice}\n")
                info("wait a couple of minutes...")
                database(5, f"{' '.join( top_coins(scan[5].split(), leverage, limit, interval, key_ema, key_roe) )}\n")

        else:
            if eval(scan[3].replace('\n', '')) == True: database(3, f"{choice}\n")

        if use:
            database(0, f"{interval}\n")
            database(1, f"{limit}\n")
            database(2, f"{leverage}\n")
            database(4, f"{' '.join( selected_coins )}\n")
            if selected_coins != []: experimental_rerun()
    
    placeholder = empty()
    update(placeholder, infinity, selected_coins, leverage, limit, interval, key_ema, key_roe, key_vol, key_price, loading, key_x)

if __name__ == "__main__": option()