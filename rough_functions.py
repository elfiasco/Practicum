from operator import index
import pandas as pd
import numpy as np
import csv
import statistics
from datetime import date, timedelta, datetime
import requests
import urllib.request, json 
import time
import random

startTime= time.time()

table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
symbols = table[0]
snp500tickers = list(symbols['Symbol'])

keys = ['TF_erfYoozEpTWRnaeEv82Gs9TPeqh7y', "vO2EDi0IWiJIj3EDfHKD0tyOcFDnQJp1", "H1B1fCRirWH0XzplhXLEk8pPbBRXdFqV", 'vI86lJ7BvliaPD3mR3rFa2tUkoXPb3zA', "ZHlX77ygc2LZ2gJEHxhwoMy2UT6z1rtQ", "Iolk3paV1L0TrVt5AaLluW1ckpD0AFaZ"]
waitT=12/len(keys)
curKey = 0

reqs=0
today = date.today()
todayMS = str(int(time.time())) 


def pullSenate():
    senatePulled = pd.read_csv("https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.csv")
    #sens = ['sen'] * len(senatePulled)
    senatePulled['sen/rep'] = 'sen'
    senatePulled['dataFound'] = 0
    senatePulled['name'] = senatePulled['senator']
    senatePulled = senatePulled.drop(['senator'], axis=1)
    senatePulled['disclosure_date'] =  pd.to_datetime(senatePulled['disclosure_date'])
    senatePulled['transaction_date'] =  pd.to_datetime(senatePulled['transaction_date'])
    senatePulled['dates_diff'] = (senatePulled['disclosure_date']-senatePulled['transaction_date']).dt.days
    senatePulled['dateMS']=(senatePulled['transaction_date']).map(pd.Timestamp.timestamp)
    senatePulled['percentVsSnP'] = 0


    senatePulled['amountL']=-1
    senatePulled['amountM']=-1
    senatePulled['amountH']=-1
    for i in range(len(senatePulled)):
        s=senatePulled['amount'][i]
        if(s=='Over $50,000,000'):
            senatePulled['amountL'][i] = 50000001
            senatePulled['amountM'][i] = 50000001
            senatePulled['amountH'][i] = 50000001
        elif(s!='Unknown'):
            s=s.replace('$', '')
            s=s.replace(',', '')
            s=s.split(' - ')
            s=(int(s[0]), int(s[1]))
            senatePulled['amountL'][i] = s[0]
            senatePulled['amountM'][i] = statistics.mean((int(s[0]), int(s[1])))
            senatePulled['amountH'][i] = s[1]
        
    senatePulled['transaction_date']=pd.to_datetime(senatePulled['transaction_date'])
    senatePulled['disclosure_date']=pd.to_datetime(senatePulled['disclosure_date'])
    senatePulled = senatePulled[senatePulled['transaction_date']<datetime(2023,1,1)]
    
    senatePulled['snp500']=0
    senatePulled.loc[senatePulled['ticker'].isin(snp500tickers).index, 'snp500']=1
    senatePulled['last_name'] = senatePulled['name'].str.split(' ').str[-1]
    senatePulled.loc[senatePulled['last_name'].str.lower().isin(['x','xi','vii','vi','v','iv','iii','ii','i','jr.','sr.','jr','sr']),'last_name'] = senatePulled.loc[senatePulled['last_name'].str.lower().isin(['x','xi','vii','vi','v','iv','iii','ii','i','jr.','sr.','jr','sr']),'name'].str.split(' ').str[-2]
    senatePulled.to_csv('senate.csv')

def pullHouse():
    housePulled = pd.read_csv("https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.csv")
    housePulled['sen/rep'] = 'rep'
    housePulled['dataFound'] = 0
    housePulled['cap_gains_over_200_usd'] = 'NA'
    housePulled['name'] = housePulled['representative']
    housePulled = housePulled.drop(['representative', 'disclosure_year'], axis=1)
    #housePulled['transaction_date'] = housePulled['transaction_date'].str.replace('-','/')
    housePulled['disclosure_date'] =  pd.to_datetime(housePulled['disclosure_date'])
    housePulled['transaction_date'] =  pd.to_datetime(housePulled['transaction_date'], errors = 'coerce')

    housePulled.loc[housePulled['type'] == 'purchase', 'type'] = "Purchase"
    housePulled.loc[housePulled['type'] == 'sale_partial', 'type'] = "Sale (Partial)"
    housePulled.loc[housePulled['type'] == 'sale_full', 'type'] = "Sale (Full)"
    housePulled.loc[housePulled['type'] == 'exchange', 'type'] = "Exchange"
    housePulled.loc[housePulled['type'] == 'sale', 'type'] = "Sale"
    
    housePulled['percentVsSnP'] = 0
    
    housePulled['amountL']=-1
    housePulled['amountM']=-1
    housePulled['amountH']=-1
    for i in range(len(housePulled)):
        s=housePulled['amount'][i]
        if(s=='$50,000,000 +'):
            housePulled['amountL'][i] = 50000001
            housePulled['amountM'][i] = 50000001
            housePulled['amountH'][i] = 50000001
        elif(s=='$1,001 -'):
            housePulled['amountL'][i] = 1000
            housePulled['amountM'][i] = 1000
            housePulled['amountH'][i] = 1000
        elif(s=='$1,000,000 +'):
            housePulled['amountL'][i] = 1000001
            housePulled['amountM'][i] = 3000000
            housePulled['amountH'][i] = 5000000
            
        elif(s!='Unknown'):
            s=s.replace('$', '')
            s=s.replace(',', '')
            s=s.split(' - ')
            s=(int(s[0]), int(s[1]))
            housePulled['amountL'][i] = s[0]
            housePulled['amountM'][i] = statistics.mean((int(s[0]), int(s[1])))
            housePulled['amountH'][i] = s[1]

    toDrop = []
    for i in range(len(housePulled)):
        if(type(housePulled['transaction_date'][i])==type(pd.NaT)):
            toDrop.append(i)
    housePulled=housePulled.drop(toDrop)  
    housePulled['dates_diff'] = (housePulled['disclosure_date']-housePulled['transaction_date']).dt.days
    housePulled['dateMS']=(housePulled['transaction_date']).map(pd.Timestamp.timestamp)
    

    housePulled['transaction_date']=pd.to_datetime(housePulled['transaction_date'])
    housePulled['disclosure_date']=pd.to_datetime(housePulled['disclosure_date'])
    housePulled = housePulled[housePulled['transaction_date']<datetime(2023,1,1)]

    housePulled['snp500']=0
    housePulled.loc[housePulled['ticker'].isin(snp500tickers).index, 'snp500']=1
    
    housePulled['last_name'] = housePulled['name'].str.split(' ').str[-1]
    housePulled.loc[housePulled['last_name'].str.lower().isin(['x','xi','vii','vi','v','iv','iii','ii','i','jr.','sr.','jr','sr']),'last_name'] = housePulled.loc[housePulled['last_name'].str.lower().isin(['x','xi','vii','vi','v','iv','iii','ii','i','jr.','sr.','jr','sr']),'name'].str.split(' ').str[-2]
    housePulled.to_csv('house.csv')

def pullData():
    pullHouse()
    pullSenate()
    senate = readSenate()
    house = readHouse()
    pd.concat([senate, house]).to_csv('data.csv')



def readSenate():
    toReturn = pd.read_csv('senate.csv')
    toReturn['disclosure_date'] =  pd.to_datetime(toReturn['disclosure_date'])
    toReturn['transaction_date'] =  pd.to_datetime(toReturn['transaction_date'])
    toReturn = toReturn.iloc[: , 1:]
    return toReturn

def readHouse():
    toReturn = pd.read_csv('house.csv')
    toReturn['disclosure_date'] =  pd.to_datetime(toReturn['disclosure_date'],)
    toReturn['transaction_date'] =  pd.to_datetime(toReturn['transaction_date'], errors = 'coerce')   
    toReturn = toReturn.iloc[: , 1:]
    return toReturn

def readData():
    toReturn = pd.read_csv('data.csv')
    toReturn['disclosure_date'] =  pd.to_datetime(toReturn['disclosure_date'], errors = 'coerce')
    toReturn['transaction_date'] =  pd.to_datetime(toReturn['transaction_date'], errors = 'coerce')   
    toReturn = toReturn.iloc[: , 1:]
    return toReturn


def freshData():
    pullData()
    return (readData())



def getTransactionsByTicker(ticker, data):
    toReturn = data[data['ticker']==ticker]
    return toReturn
def getTransactionsByPerson(name, data):
    toReturn = data[data['name']==name]
    return toReturn
def getTransactionsByType(type, data):
    toReturn = data[data['type']==type]
    return toReturn


def stockPriceOnDay(ticker, day):
    global curKey
    global reqs
    time.sleep(waitT)
    key=keys[curKey]
    uri = 'https://api.polygon.io/v1/open-close/'+str(ticker)+'/'+str(day)+'?adjusted=true&apiKey='+key
    curKey=curKey+1
    if(curKey==len(keys)):
        curKey=0
    r = requests.get(url = uri)
    reqs=reqs+1
    d = r.json()

    if(d['status']=='OK'):
        return((float(d['high'])+float(d['low']))/2)
    elif(d['status']=='NOT_FOUND'):
        return (str(d['message']))
    elif(d['status']=='ERROR'):
        return (d['error'])

def currentValueOfTrade(dataIndex, data, amountType='amountM', stockPriceToday=0):
    if(type(stockPriceToday)==str):
        return stockPriceToday
    ticker = data['ticker'][dataIndex]
    amount = data[str(amountType)][dataIndex]
    t = data['type'][dataIndex]
    transactionDay = data['transaction_date'][dataIndex]

    priceOnTransactionDay=stockPriceOnDay(data['ticker'][dataIndex], transactionDay)
    if (type(priceOnTransactionDay)==str):
        return (priceOnTransactionDay)
    if(stockPriceToday==0):
        stockPriceToday=stockPriceOnDay(ticker, today-timedelta(days=9))
    return (amount*(stockPriceToday/priceOnTransactionDay))



def originalValueOfTrade(dataIndex, data, amountType='amountM'):
    return(data[str(amountType)][dataIndex])

def transactionDateOfTrade(dataIndex, data):
    return(data['transaction_date'][dataIndex])

def curSnP():
    ticker="%5EGSPC"
    url="https://query1.finance.yahoo.com/v8/finance/chart/"+ticker+"?period1="+todayMS+"&period2="+todayMS+"&interval=1d"
    with urllib.request.urlopen(url) as url:
        data = json.load(url)
        df = pd.json_normalize(data['chart']['result'])
        todayPrice = (df['meta.regularMarketPrice'])
    return(todayPrice[0])



def percentChangeOfSnP(pastDate, newDate=todayMS, curSNP='false'):
    if (curSNP!='false'):
        newPrice = curSNP
    else:
        newPrice = curSnP()
    d = pd.read_csv('SnP500Data.csv')
    oldPrice =(d[d['Date']==pastDate])
    oldPrice = oldPrice['Open'].iloc[0]
    toReturn=newPrice/oldPrice
    return(toReturn)

# SnPToday = curSnP()
# currentStockPrices = dict()

def vsSNPPercent(dataIndex, data, currentStockPrices='none'):
    if (currentStockPrices=='none'):
        stockPriceT = stockPriceOnDay(data['ticker'][dataIndex], today-timedelta(days=9)); #time.sleep(waitTime)
        currentStockPrices[data['ticker'][dataIndex]] = stockPriceT
        
    else:
        stockPriceT=currentStockPrices.get(data['ticker'][dataIndex],'none')
        if (stockPriceT=='none'):
            stockPriceT = stockPriceOnDay(data['ticker'][dataIndex], today-timedelta(days=9)); #time.sleep(waitTime)
            currentStockPrices[data['ticker'][dataIndex]] = stockPriceT
    currentValue = currentValueOfTrade(dataIndex, data, stockPriceToday=stockPriceT); #time.sleep(waitTime)
    if (type(currentValue)==str):
        
        return (currentValue, currentStockPrices)
    else:
        stat =(currentValue/originalValueOfTrade(dataIndex,data))-percentChangeOfSnP(transactionDateOfTrade(dataIndex, data), curSNP=SnPToday)
        if (data['type'][dataIndex]!='Purchase'):
            stat=stat*(-1)


        
        return(stat, currentStockPrices)

def run():
    data=readData()

    data=data[data['ticker']!='--']
    dataLen=len(data)



    #data = getTransactionsByType('Purchase', data)
    indexes = data.index.tolist()
    random.shuffle(indexes)
    counterPos = 0
    counterDataFound = 0
    postEvery=1
    iterations=0
    #print(percentChangeOfSnP(data['transaction_date'][10], todayMS))


    for i in indexes:

        if ([data['dataFound']==0]):
            iterations=iterations+1
            out, currentStockPrices = vsSNPPercent(i, data, currentStockPrices)

            if (out=="You've exceeded the maximum requests per minute, please wait or upgrade your subscription to continue. https://polygon.io/pricing"):
                print(out)
                break
            if (out!="Data not found."):
                
                amountString = ""
                if(abs(out)>.5):
                    amountString = " ($"+str(round(data['amountM'][i]-.5))+")"
                print(str(i)+": "+str(data['ticker'][i])+": "+str(round(100*out, 2))+"%"+amountString)
                counterDataFound=counterDataFound+1
                data.at[i,'percentVsSnP']=out
                data.at[i,'dataFound']=1
                if (out>0):
                    counterPos=counterPos+1
            else:
                data.at[i,'dataFound']=404
                
            if (counterDataFound==postEvery):
                data.to_csv('data.csv') #AUTOSAVE
                postEvery=postEvery+10
                totalFound = 0
                
                totalWon = 0
                net=0
                
                dd=data[data['dataFound']==1]

                indexess = dd.index.tolist()
                for ii in indexess:
                    totalFound=totalFound+1
                    if(float(dd['percentVsSnP'][ii])>0):
                        totalWon=totalWon+1
                    net=net+(float(dd['percentVsSnP'][ii])*dd['amountM'][ii])
                secondsPassed=int(time.time()-startTime)
                minutesPassed=int(secondsPassed/60)
                p=totalWon/len(dd)
                sd=((p*(1-p))/totalFound)**(.5)
                print("")
                print("UPDATED POPULATION STATS")
                #print("Percent Won: "+str(100*round(p, 2))+"%")
                print("     Bernoulli P 95% Confidence Interval: ("+str(round(p-(2*sd), 4))+", "+str(round(p+(2*sd), 4))+"). N="+str(totalFound)   )
                ##print("     Net Profits: $"+str(round(net, 2)))
                print("     Median Percent Profit: 0"+str(round(100*dd['percentVsSnP'].median(), 4))+"%")
                print("     Percent of Iterations Completed: "+str(round(100*len(data[data['dataFound']!=0])/dataLen, 2))+"%")
                print("")
                print("CURRENT ITERATION STATS")
                print("     Total Iterations: "+str(iterations)+". Iterations w/ Data Found: "+str(counterDataFound))
                print("     Time: "+str(round(minutesPassed/60))+"hr "+str(minutesPassed%60)+"min "+str(secondsPassed%60)+"sec. Requests/Minute: "+str(round(reqs/secondsPassed*60,2)))

                
                print("")
                print("ID:  TICKER:  S&P500 ADJ. EARNINGS")



#run()




#data = readData()
#print(getTransactionsByTicker('AMZN', readData())['amount'].unique())









#person, sen/rep, ticker, amount, asset_discription, type, transaction_date, disclosure_date, owner, cap_gains_over_200_usd, ptr_link