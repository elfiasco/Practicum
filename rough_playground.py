from operator import index
import pandas as pd
import numpy as np
import csv
import statistics
from datetime import date, timedelta
import requests
import urllib.request, json 
import time
import random
import matplotlib.pyplot as plt


def readData():
    toReturn = pd.read_csv('data.csv')
    toReturn = toReturn.iloc[: , 1:]
    return toReturn

data = readData()
# data=data[data['dataFound']==1]
# data=data[data['type']!='Purchase']




#print(data['percentVsSnP'].mean)

# plt.hist(data['percentVsSnP'], range=(-1, 1), bins=20)
# plt.axvline(data['percentVsSnP'].mean(), color='k', linestyle='dashed', linewidth=1)
# plt.axvline(data['percentVsSnP'].median(), color='c', linestyle='dashed', linewidth=1)
# plt.show()

# names = data['name'].unique()

# means = {}
# medians = {}
# totalAmountM = {}
# for name in names:
#     dataByName = data[data['name']==name]
#     totalAmountM[name] = dataByName['amountM'].sum()
#     if (len(dataByName)>10):
        
#         means[' '.join(name.split())] = dataByName['percentVsSnP'].mean()
#         medians[' '.join(name.split())] = dataByName['percentVsSnP'].median()

# #print (totalAmountM)
# #print("Max Mean: "+str(max(means, key=means.get))+": "+str(means[max(means, key=means.get)])+". N="+str(len(data[data['name']==max(means, key=means.get)])))
# #print("Max Median: "+str(max(medians, key=medians.get))+": "+str(medians[max(medians, key=medians.get)])+". N="+str(len(data[data['name']==max(means, key=medians.get)])))



# #print(data['percentVsSnP'].mean())
# #print(data['percentVsSnP'].median())
# #print(totalAmountM.get("Hon. Mark Green"))
# data['percentOfPortfolio'] = data['amountM']

# indexes = data.index.tolist()
# for d in indexes:
#     data['percentOfPortfolio'][d]=data['percentOfPortfolio'][d]/totalAmountM.get(data['name'][d])

# data.to_csv('dataFound.csv')



# # for d in means:
# #     print(d+": "+str(round(means.get(d),4)))


# # print("Max Mean: "+str(max(means, key=means.get))+": "+str(means[max(means, key=means.get)])+". N="+str(len(data[data['name']==max(means, key=means.get)])))
# # print("Max Median: "+str(max(medians, key=medians.get))+": "+str(medians[max(medians, key=medians.get)])+". N="+str(len(data[data['name']==max(means, key=medians.get)])))


# # meanList = list(means.values())
# # plt.hist(meanList, range=(-.3, .3), bins=20)
# # plt.show()


# def histByName(name):
#     d=data[data['name']==name]
#     l=list(d['percentVsSnP'])
#     plt.hist(l, range=(-1, 1), bins=20)
#     plt.title(name)
#     plt.show()

# #histByName('Thomas H Tuberville')

# winners = []
# for m in means:
#     if (means.get(m)>.008) and len(data[data['name']==m])>30:
#         winners.append(m)
#         #print (str(m)+": "+str(means.get(m))+". N="+str(len(data[data['name']==m])))

# win = data[data['name'].isin(winners)]

# plt.hist(list(win['percentVsSnP']), range=(-1, 1), bins=20)
# plt.axvline(win['percentVsSnP'].mean(), color='k', linestyle='dashed', linewidth=1)
# plt.title("N="+str(len(winners))+' Obs.='+str(len(win))+', mean='+str(win['percentVsSnP'].mean()))
# #plt.show()
# #print(winners)

# #data = csv.read('dataFound.csv')
# # gb = data.groupby('name')    
# # for x in gb.groups:


# greater = 0
# for i in means:
#     if means.get(i)>0:
#         greater=greater+1

# print(greater/len(means))


print(len(data['ticker'].unique()))
