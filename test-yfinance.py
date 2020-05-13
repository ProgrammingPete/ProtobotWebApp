#Test yfinance
# THis function literally scrapes the data from yahoo's website... 



import yfinance as yf

msft = yf.Ticker("VTIQ")


hist = msft.history(period="max")

# finances = msft.get_balancesheet();
info = msft.get_info()
#print(finances)