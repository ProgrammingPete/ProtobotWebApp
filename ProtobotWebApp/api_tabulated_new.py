from binance.client import Client
import time
from datetime import datetime
import pandas as pd
import threading

def rawtab():
    indicator = False
    while True:
        for pair in trading_pairs:
            kline = client.get_klines(symbol=pair, interval='1m', limit=10)
            entry = dict()
            entry['trading pair'] = pair
            kline[0][0] = datetime.utcfromtimestamp((kline[0][0]/1000) - 5*3600).strftime('%Y/%m/%d %H:%M:%S')
            kline[0][6] = datetime.utcfromtimestamp((kline[0][6]/1000) - 5*3600).strftime('%Y/%m/%d %H:%M:%S')

            for i, label in enumerate(labels):
                entry[label] = kline[0][i]

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


        print(rawtable)
        #print(len(rawtable))
        time.sleep(interval_seconds)


def write_to_csv(entry):
        print("Setting the Table")
        tab = pd.DataFrame(entry).reindex(columns = labels)
        file = open('rawtab.csv', 'a')
        tab.to_csv(file , mode= 'a', header= False)
        file.close()

def calcMovAvg(rawtable):
        averageMov_ten, averageMov_twenty, total = int(), int(), int()
        length = len(rawtable)
        j = length / 2
        for i, entry in enumerate(rawtable):
            div2i = i / 2
            total += float(entry['Close Price'])
            if j == (i + 1):
                #print("i // 2: ",  i / 2)
                averageMov_ten = total / j
        averageMov_twenty = total / length
        print("Moving averages= 10: %f, 20: %f " % (averageMov_ten, averageMov_twenty))
        return averageMov_ten, averageMov_twenty

api_key = 'cPm5GZKAa60eT8cvkMbrhkvQN9ZkYPCDDS9sJ9VHgceOdXPHYsJcEqsmCaSIFJjr'#generated from binance
api_secret = 'SBv8xWd1hu0djnFYZjE9lJJNROohaeyDyyAJdGp7htK64uPcALWJTS4L2swjFUac'#generated from binance
client = Client(api_key,api_secret)

interval_seconds = 60
trading_pairs = ['BTCUSDT']
threads = list()
rawtable = list()  # shared resource

# this function get_klines returns a kline with a list of:
# Open Time
# Open Price
# High
# Low
# Close Price
# Volume
# close time
# Taker buy base asset volume: Volume of the first part of the pair (BTC)
# Taker buy quote asset volume : Volume of the second part of the pair (USDT)
labels = ['Open Time','Open Price','High', 'Low', 'Close Price',
          'Volume', 'Close time', 'Quote asset volume','Number Of Trades',
          'Taker buy base', 'Taker buy quote' ]

