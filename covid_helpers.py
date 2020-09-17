#!/usr/bin/env python
# coding: utf-8

# In[4]:


import numpy as np
import pandas as pd
import datetime as dt
from IPython.display import clear_output
import requests
import ipywidgets as widgets
from ipywidgets import interact, interact_manual
import os
import csv

try:
    import matplotlib.pyplot as plt
except:
    get_ipython().system('pip install matplotlib')
    clear_output()
    import matplotlib.pyplot as plt

try:
    import xlrd
except:
    get_ipython().system('pip install xlrd')
    clear_output()
    import xlrd

try:
    import mplcyberpunk
except:
    get_ipython().system('pip install mplcyberpunk')
    clear_output()
    import mplcyberpunk

plt.style.use("cyberpunk")

try:
  import nbinteract as nbi
except:
  get_ipython().system('pip install nbinteract')
  clear_output()
  import nbinteract as nbi


# In[3]:


def csv_from_excel(filename,sheetname):
    wb = xlrd.open_workbook(filename+'.xlsx')
    sh = wb.sheet_by_name(sheetname)
    your_csv_file = open(filename+'.csv', 'w')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    your_csv_file.close()


# In[4]:


dailycases = requests.get('https://opendata.ecdc.europa.eu/covid19/casedistribution/csv')

if dailycases.status_code == 200:
    with open('dailycases.csv', 'wb') as f:
        f.write(dailycases.content)


# In[5]:


testingdata = requests.get('https://www.ecdc.europa.eu/sites/default/files/documents/weekly_testing_data_EUEEAUK_2020-09-16.xlsx')

if testingdata.status_code == 200:
    with open('testingdata.xlsx', 'wb') as f:
        f.write(testingdata.content)

wb = xlrd.open_workbook('testingdata.xlsx')
# print(wb.sheet_names())

csv_from_excel('testingdata','Sheet1')


# In[6]:


dog = dt.date.today() - dt.timedelta(days=1)


# In[7]:


ndays = 0

while not pd.isna(ndays):
  date = dt.date.today() - ndays*dt.timedelta(days=1)

  hospitaldata = requests.get('https://www.ecdc.europa.eu/sites/default/files/documents/hosp_icu_all_data_'+str(date)+'.xlsx')

  if hospitaldata.status_code == 200:
      ndays = np.nan
      with open('hospitaldata.xlsx', 'wb') as f:
          f.write(hospitaldata.content)
  else:
    ndays = ndays+1

wb = xlrd.open_workbook('hospitaldata.xlsx')
# print(wb.sheet_names())

csv_from_excel('hospitaldata','Sheet1')


# In[8]:


year = dt.date.today().isocalendar()[0]
week = dt.date.today().isocalendar()[1]

while not np.isnan(week):
  deathdata = requests.get('https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/healthandsocialcare/causesofdeath/datasets/deathregistrationsandoccurrencesbylocalauthorityandhealthboard/'+str(year)+'/lahbtablesweek'+str(week)+'.xlsx')
  
  if deathdata.status_code == 200:
      week = np.nan
      with open('deathdata.xlsx', 'wb') as f:
          f.write(deathdata.content)
  else:
#     print(week)
    week = week - 1
wb = xlrd.open_workbook('deathdata.xlsx')
# print(wb.sheet_names())

csv_from_excel('deathdata','Registrations - All data')


# In[9]:


cases = pd.read_csv('dailycases.csv')
tests = pd.read_csv('testingdata.csv')
hospital = pd.read_csv('hospitaldata.csv')
death = pd.read_csv('deathdata.csv')


# In[10]:


death.columns = death.iloc[2].values
death = death[3:]


# In[12]:


cases.index = [dt.datetime(year,month,day) for year,month,day
               in zip(cases.year.values,cases.month.values,cases.day.values)]

week = dt.timedelta(days=7)
tests.index = [dt.datetime(2020,1,6)+week*(int(i[-2:])-2)
               if int(i[-2:]) != 1 else dt.datetime(2020,1,1)
               for i in tests.year_week]

hospital['datetime'] = [dt.datetime.strptime(i,'%Y-%m-%d') if not pd.isna(i) else
                        dt.datetime(2020,1,6)+week*(int(j[-2:])-2)
                        if int(j[-2:]) != 1 else dt.datetime(2020,1,1)
                        for i,j in zip(hospital.date,hospital.year_week)]

death.index = [dt.datetime(2020,1,6)+week*(int(float(i))-2)
               if int(float(i)) != 1 else dt.datetime(2020,1,1)
               for i in death['Week number'].values]

cases.to_csv('dailycases.csv')
tests.to_csv('testingdata.csv')
hospital.to_csv('hospitaldata.csv')
death.to_csv('deathdata.csv')

