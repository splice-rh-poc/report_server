#!/usr/bin/python
import datetime

start_date = raw_input("Enter a start date as.. yyyy mm dd hh \n")
print('you entered ', start_date)
sd = datetime.datetime.strptime(start_date, "%Y %m %d %H")

end_date = raw_input("Enter an end date as.. yyyy mm dd hh \n")
print('you entered ', end_date)
ed = datetime.datetime.strptime(end_date, "%Y %m %d %H")


print(str(ed -sd))