#!/usr/bin/python
from datetime import date, datetime, timedelta
import datetime

from common import config

'''
start_date = input("Enter a start date as.. yyyy mm dd hh \n")
print('you entered ', start_date)

end_date = input("Enter an end date as.. yyyy mm dd hh \n")
print('you entered ', end_date)

Double check w/ http://www.timeanddate.com/date/timeduration.html
'''

def datespan_by_hour(startDate, endDate):
    return datespan(startDate, endDate)

def datespan_by_day(startDate, endDate):
    return datespan(startDate, endDate, delta=timedelta(days=1))

def datespan_by_4hour(startDate, endDate):
    return datespan(startDate, endDate, delta=timedelta(hours=4))

def datespan(startDate, endDate, delta=timedelta(hours=1)):
    currentDate = startDate
    count = 0
    last_month_days = 0
    hours_for_sub = {}
    total_hours = 0
    while currentDate <= endDate:
        hours_for_sub[currentDate.month] = {}
        hours_for_sub[currentDate.month]['start'] = startDate
        if (currentDate + delta).month > currentDate.month :
            sub = count 
            
            hours_for_sub[currentDate.month]['hours_for_sub'] = sub
            hours_for_sub[currentDate.month]['end'] = currentDate
            count = 0
            startDate = currentDate + delta
        
        if currentDate.month == endDate.month:
            last_month_days += 1
            sub = last_month_days 
            hours_for_sub[currentDate.month]['hours_for_sub'] = sub
            hours_for_sub[currentDate.month]['end'] = currentDate
            
        count += 1
        currentDate += delta
    for key, value in hours_for_sub.items():
        print(key, value['start'], value['end'], value['hours_for_sub'])
        total_hours += value['hours_for_sub']
    
    return total_hours


config.init()

start_date = "2012 01 01 00"
end_date = "2012 02 01 00"
sd = datetime.datetime.strptime(start_date, "%Y %m %d %H")
#ed = datetime.datetime.strptime(end_date, "%Y %m %d %H")
ed = datetime.datetime.now()



print('#'*6 + 'HOUR' + '#'*6)
print datespan_by_hour(sd, ed)
print('#'*6 + 'HOUR' + '#'*6)
print('')
    
print('#'*6 + 'DAY' + '#'*6)
print datespan_by_day(sd, ed)
print('#'*6 + 'DAY' + '#'*6)
    
    
print('#'*6 + '4hr' + '#'*6)
print datespan_by_4hour(sd, ed)
print('#'*6 + '4hr' + '#'*6)