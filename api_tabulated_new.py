from binance.client import Client
from binance.helpers import date_to_milliseconds, interval_to_milliseconds
import time
from datetime import datetime
import pandas as pd
import threading
import os


def rawtab(filename = 'rawtab_BTCUSDT.csv', pair = 'BTCUSDT'):
    """
    Method that is run within a thread.
    Maintains a data structure (list of dictionaries) in plain old memory.
    """
    indicator = False
    count = 0
    interval_seconds = 60 
    #with lock:
    update_csv(filename, pair)
    while True:
        count = count + 1
        #check status of binance server
        if check_status():
            supported_pairs[pair].append({'Error' : 'binance_server_maintenance'})
            break

        #fetch kline from binance and convert format to ours
        klines = client.get_klines(symbol=pair, interval='1m', limit=1)
        for kline in klines:
            entry = convert_format(kline,pair)
        
        # add entry to rawtab
        supported_pairs[pair].append(entry)
        print(supported_pairs[pair], threading.current_thread().name)

        if len(supported_pairs[pair]) > 20:
            entry = supported_pairs[pair].pop(0) # keep table at 20 entries (might remove this)
            if count == 20: # save new klines to file
                count = count / 20
                update_csv(filename, pair)
                #print('Write here')
                    
            tenSMA, twentySMA = calcMovAvg(supported_pairs[pair]) # do some data calc sheit
            if tenSMA > twentySMA:
                indicator = True# buy
            else:
                indicator = False# sell
            # this looks horrendous lol, but we add it to the current entry
            supported_pairs[pair][-1]['indicator']  = str(indicator)
            supported_pairs[pair][-1]['10-SMA']  = str(tenSMA)
            supported_pairs[pair][-1]['20-SMA']  = str(twentySMA)
        else:
            supported_pairs[pair][- 1]['indicator']  = str(indicator)
            supported_pairs[pair][- 1]['10-SMA']  = 0
            supported_pairs[pair][- 1]['20-SMA']  = 0

        time.sleep(interval_seconds)


def write_to_csv(entry,filename):
        tab = pd.DataFrame(entry)
        with  open(filename, 'a') as file:
            tab.to_csv(file , mode= 'a', header= False )

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
    Klines are uniquely identified by their open_time.
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
    outputTab = list()
    if check_status():
        return {'error' : 'Binance_server_maintenance'} 
    with lock:
        klines = client.get_historical_klines(symbol=currency, interval=kline_length,start_str= start_time, end_str=end_time )
    for kline in klines:
        outputTab.append(convert_format(kline, currency))
    return outputTab 

def convert_format(kline, pair):
    entry = dict()
    entry['trading_pair'] = pair  
    #print(kline[0],type(kline[0]))
    kline[0] = datetime.utcfromtimestamp((kline[0])/1000).strftime('%Y/%m/%d %H:%M:%S')
    kline[6] = datetime.utcfromtimestamp((kline[6])/1000).strftime('%Y/%m/%d %H:%M:%S')
    for i, label in enumerate(labels):
        entry[label] = kline[i]
    return entry

def check_status():
        """Status of the Binance system. Response is either a 0 or 1."""
        response = client.get_system_status()
        return response['status']

def reverse_readline(filename, buf_size=8192):
    """A generator that returns the lines of a file in reverse order"""
    with open(filename) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first 
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1): # reverses the line
                if lines[index]:
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment

def update_csv(filename, pair = 'BTCUSDT', interval = '1m'):
    """Update the save Klines"""
    print("Updating CSV")
    last_line = next(reverse_readline(filename)).split(',') # use the reverse generator
    time = date_to_milliseconds(last_line[7]) + interval_to_milliseconds(interval)  #get last missed kline open time
    klines_diff = client.get_historical_klines(pair,'1m', time) # fetch difference from api
    #print(klines_diff)
    for kline in klines_diff: # write new klines to file
        print(kline)
        kline = convert_format(kline, pair)
        write_to_csv([kline], filename)

### shared resources #######
api_key = 'cPm5GZKAa60eT8cvkMbrhkvQN9ZkYPCDDS9sJ9VHgceOdXPHYsJcEqsmCaSIFJjr'#generated from binance
api_secret = 'SBv8xWd1hu0djnFYZjE9lJJNROohaeyDyyAJdGp7htK64uPcALWJTS4L2swjFUac'#generated from binance
client = Client(api_key,api_secret)

rawtab_BTCUSDT = list()
rawtab_ETHUSDT = list()
#rawtab_ETCUSDT = list()
supported_pairs = {'BTCUSDT' : rawtab_BTCUSDT,
                   'ETHUSDT' : rawtab_ETHUSDT}
lock = threading.Lock()  
labels = ['Open_Time','Open_Price','High', 'Low', 'Close_Price',
          'Volume', 'Close_time', 'Quote_asset_volume','Number_Of_Trades',
          'Taker_buy_base', 'Taker_buy_quote' ]

