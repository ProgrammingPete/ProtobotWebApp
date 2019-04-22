from  api_tabulated_new import  write_to_csv, convert_format,  get_from_csv
from datetime import datetime
from binance.helpers import date_to_milliseconds

def update_panels():
    interval =[30,7,1] 
    pairs = ['BTCUSDT', 'ETHUSDT']
    for pair in pairs:    
        print('on pair', pair)
        for i in interval:    
            date_now = date_to_milliseconds('now')//(1000)
            #print(date_now)
            date = datetime.utcfromtimestamp(date_now - i*86400).strftime('%Y/%m/%d %H:%M:00')
            #print(date)
            print('On interval days:', i)
            table = get_from_csv(pair, date, 'now', True)
            print('writing ot file')
            file_to_write = 'prerendered/pre' + pair + str(i) +  '.csv'
            write_to_csv(table, file_to_write, append = False)
    print('Finished updating prerendered files')


if __name__ == '__main__':
    update_panels()




