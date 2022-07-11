from tradingview_ta import TA_Handler, Interval
import threading
import time

tmr = 0
symbols = ['btcusdt', 'rlcusdt', 'opusdt', 'crvusdt', 'linkusdt']

def func():
    
    print()
    global tmr 
    tmr += 1

    for symbol in symbols:
        output = TA_Handler(symbol=symbol, screener = 'crypto', exchange = 'BINANCE', interval = Interval.INTERVAL_15_MINUTES)
        print(time.strftime("%H:%M:%S",  time.localtime()), symbol + f' {tmr} : ' + 
        output.get_analysis().summary['RECOMMENDATION'], ": N/B/S :", 
        round((100/26)*output.get_analysis().summary['NEUTRAL'], 2), "% /", 
        round((100/26)*output.get_analysis().summary['BUY'], 2), "% /", 
        round((100/26)*output.get_analysis().summary['SELL'], 2), "%")

    threading.Timer(15.0, func).start()  # Restart after 15 seconds

func()
