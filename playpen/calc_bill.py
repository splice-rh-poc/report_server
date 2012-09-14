#!/usr/bin/python
from datetime import date, datetime, timedelta
import datetime

'''
start_date = input("Enter a start date as.. yyyy mm dd hh \n")
print('you entered ', start_date)

end_date = input("Enter an end date as.. yyyy mm dd hh \n")
print('you entered ', end_date)
'''

def datespan(startDate, endDate):
    delta=timedelta(hours=1)
    currentDate = startDate
    count = 0
    last_month_days = 0
    hours_for_sub = {}
    while currentDate < endDate:
        hours_for_sub[currentDate.month] = {}
        hours_for_sub[currentDate.month]['start'] = startDate
        if (currentDate + delta).month > currentDate.month :
            sub = count 
            
            hours_for_sub[currentDate.month]['sub'] = sub
            hours_for_sub[currentDate.month]['end'] = currentDate
            count = 0
            startDate = currentDate + delta
        
        if currentDate.month == endDate.month:
            last_month_days += 1
            sub = last_month_days 
            hours_for_sub[currentDate.month]['sub'] = sub
            hours_for_sub[currentDate.month]['end'] = currentDate
            
        count += 1
        currentDate += delta
    for key, value in hours_for_sub.items():
        print(key, value['start'], value['end'], value['sub'])
        #print(key, str(value['start']), str(value['end']), str(value['sub']))
    return hours_for_sub

def datespan_count(startDate, endDate, delta=timedelta(hours=1)):
    currentDate = startDate
    count = 0
    while currentDate < endDate:
        count += 1
        currentDate += delta
    return count


start_date = "2012 01 05 05"
end_date = "2012 0 01 06"
sd = datetime.datetime.strptime(start_date, "%Y %m %d %H")
#ed = datetime.datetime.strptime(end_date, "%Y %m %d %H")
ed = datetime.datetime.now()



for day in datespan(sd, ed):
    print(day)
    
#print(datespan_count(sd, ed))