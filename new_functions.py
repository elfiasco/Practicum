import yfinance as yf
import pandas as pd
def list_diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

def end_of_day_data_builder(tickers, start="2012-06-19", end="2022-12-31"): ##This takes around 6 minutes
    #build formatted string of tickers to feed into yfinance api
    
    ticker_str = tickers[0]
    for ticker in tickers[1:]:
        ticker_str=ticker_str+" "+ticker
    #next, get unavalible tickers
    yfdata = yf.download(ticker_str, start="2022-12-30", end="2022-12-31")
    yfdata=yfdata['Adj Close']
    unavalible = list((yfdata.loc[list(yfdata.index)[0],:][yfdata.loc[list(yfdata.index)[0],:].isna()]).index)
    #remove unavalible tickers from our list
    tickers = list_diff(list(tickers),list(unavalible))
    ticker_str = tickers[0]
    for ticker in tickers[1:]:
        ticker_str=ticker_str+" "+ticker
    #now, get all the data we can, this will take a loooooong time
    yfdata = yf.download(tickers, start=start, end=end)
    yfdata=yfdata['Adj Close']

    #return dataframe (after saving it) and list of unavalible tickers
    yfdata.to_csv('EODdata.csv')
    return yfdata, unavalible


