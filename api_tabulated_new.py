from binance.client import Client
import time
from datetime import datetime
import pandas as pd
import threading

def rawtab():
    indicator = False
    interval_seconds = 60
    trading_pairs = ['BTCUSDT']
    while True:
        #heck status of binance server
        if check_status():
            rawtab.append({'error' : 'Binance Server Maitenance'})

        for pair in trading_pairs:
            klines = client.get_klines(symbol=pair, interval='1m', limit=1)
            print(klines)
            entry = convert_format(klines,pair)[0]
            rawtable.append(entry)

        if len(rawtable) > 20:
            entry = rawtable.pop(0)
            write_to_csv([entry])
            tenSMA, twentySMA = calcMovAvg(rawtable)
            if tenSMA > twentySMA:
                indicator = True# buy
            else:
                indicator = False# sell
            rawtable[len(rawtable) - 1]['indicator']  = str(indicator)
            rawtable[len(rawtable) - 1]['10-SMA']  = str(tenSMA)
            rawtable[len(rawtable) - 1]['20-SMA']  = str(twentySMA)
        else:
            rawtable[len(rawtable) - 1]['indicator']  = str(indicator)
            rawtable[len(rawtable) - 1]['10-SMA']  = 0
            rawtable[len(rawtable) - 1]['20-SMA']  = 0

        #print(rawtable)
        #print(len(rawtable))
        time.sleep(interval_seconds)


def write_to_csv(entry):
        print("Setting the Table")
        tab = pd.DataFrame(entry).reindex(columns = labels)
        file = open('rawtab.csv', 'a')
        tab.to_csv(file , mode= 'a', header= False )
        file.close()

def calcMovAvg(rawtable):
        averageMov_ten, averageMov_twenty, total = int(), int(), int()
        length = len(rawtable)
        j = length / 2
        for i, entry in enumerate(rawtable):
            total += float(entry['Close_Price'])
            if j == (i + 1):
                #print("i // 2: ",  i / 2)
                averageMov_ten = total / j
        averageMov_twenty = total / length
        #print("Moving averages= 10: %f, 20: %f " % (averageMov_ten, averageMov_twenty))
        return averageMov_ten, averageMov_twenty

def get_historical(start_time, end_time, kline_length='1m', currency = "BTCUSDT"):
    """
    This function will use Binance API to fetch historical data for specified currenncy. 
    For now, start time and end time can be a time or "10 hours ago", "now"
    One kline data example: 
            .. code-block:: python

            [
                [
                    1499040000000,      # Open time
                    "0.01634790",       # Open
                    "0.80000000",       # High
                    "0.01575800",       # Low
                    "0.01577100",       # Close
                    "148976.11427815",  # Volume
                    1499644799999,      # Close time
                    "2434.19055334",    # Quote asset volume
                    308,                # Number of trades
                    "1756.87402397",    # Taker buy base asset volume
                    "28.46694368",      # Taker buy quote asset volume
                    "17928899.62484339" # Can be ignored
                ]
            ]
    """
    if check_status():
        return {'error' : 'Binance Server Maitenance'} 
    klines = client.get_historical_klines(symbol=currency, interval=kline_length,start_str= start_time, end_str=end_time )
    return convert_format(klines, currency)

def convert_format(klines, pair):
    """Klines needs to be a list of lists"""
    output = list()
    for kline in klines:
        entry = dict()
        entry['trading_pair'] = pair   
        kline[0] = datetime.utcfromtimestamp((kline[0])/1000).strftime('%Y/%m/%d %H:%M:%S')
        kline[6] = datetime.utcfromtimestamp((kline[6])/1000).strftime('%Y/%m/%d %H:%M:%S')
        for i, label in enumerate(labels):
            entry[label] = kline[i]
        #print(entry)
        output.append(entry)
        #print("{} \n ".format(output))
    return output

def check_status():
        """Status of the Binance system. Response is either a 0 or 1."""
        response = client.get_system_status()
        return response['status']

api_key = 'cPm5GZKAa60eT8cvkMbrhkvQN9ZkYPCDDS9sJ9VHgceOdXPHYsJcEqsmCaSIFJjr'#generated from binance
api_secret = 'SBv8xWd1hu0djnFYZjE9lJJNROohaeyDyyAJdGp7htK64uPcALWJTS4L2swjFUac'#generated from binance
client = Client(api_key,api_secret)

rawtable = list()  # shared resource

labels = ['Open_Time','Open_Price','High', 'Low', 'Close_Price',
          'Volume', 'Close_time', 'Quote_asset_volume','Number_Of_Trades',
          'Taker_buy_base', 'Taker_buy_quote' ]

