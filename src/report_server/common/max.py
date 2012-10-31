# Copyright  2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from __future__ import division
from report_server.sreport.models import  ReportData, ReportDataDaily

import logging
from report_server.common.custom_count import Rules
from datetime import datetime, timedelta
from report_server.common import constants



_LOG = logging.getLogger(__name__)
rules = Rules()
report_biz_rules = rules.get_rules()

class MaxUsage:
    
    
    @staticmethod
    def get_MDU_MCU(start, end, contracted_use, filter_args, product_config):
        count_list = []
        f = filter_args
        delta=timedelta(days=1)
        currentDate = start
        calculation = product_config['calculation']
        contracted_use = contracted_use
        results = []
        mdu_count = []
        mcu_count = []
        daily_highest_concurrent_usage = 0
        
        
        
        while currentDate < end:
            hourly_highest_concurrent_usage = 0
            day = currentDate.strftime(constants.day_fmt)
            if calculation == 'hourly':
                mdu_each = ReportData.objects.filter(day=day, **filter_args).distinct("instance_identifier")
                mdu = len(mdu_each)
                
            elif calculation == 'daily':
                mdu = ReportDataDaily.objects.filter(day=day, **filter_args).count()
            else:
                _LOG.error('check rules, unsupported format found != hourly,daily')
                raise Exception("unsupported calculation")
            
            
            hour_delta = timedelta(hours=1)
            currentHour = currentDate
            for h in range(24):
                this_hour = currentHour.strftime(constants.hr_fmt)
                mcu = ReportData.objects.filter(hour=this_hour, **filter_args).count()
                if mcu > hourly_highest_concurrent_usage:
                    hourly_highest_concurrent_usage = mcu
                
                currentHour += hour_delta
                
            #The highest number is the count
            mcu = hourly_highest_concurrent_usage
            
            results.append({'date': currentDate.strftime(constants.just_date), 'mdu': mdu, 'mcu': mcu})
            mdu_count.append(mdu)
            mcu_count.append(mcu)
            currentDate += delta
        
        return results, mdu_count, mcu_count
    
    
    
    @staticmethod
    def get_MDU(start, end, contracted_use, filter_args, product_config):
        count_list = []
        f = filter_args
        delta=timedelta(days=1)
        currentDate = start
        calculation = product_config['calculation']
        contracted_use = contracted_use
        results = []
        justCount = []
        while currentDate < end:
            day = currentDate.strftime(constants.day_fmt)
            if calculation == 'hourly':
                count = ReportData.objects.filter(day=day, **filter_args).count()
            elif calculation == 'daily':
                count = ReportDataDaily.objects.filter(day=day, **filter_args).count()
            else:
                _LOG.error('check rules, unsupported format found != hourly,daily')
                raise Exception("unsupported calculation")
            results.append({'date': currentDate.strftime(constants.just_date), 'count': count})
            justCount.append(count)
            currentDate += delta
        
        return results, justCount
    
    @staticmethod
    def get_MCU(start, end, contracted_use, filter_args, product_config):
        count_list = []
        f = filter_args
        delta=timedelta(days=1)
        currentDate = start
        calculation = product_config['calculation']
        contracted_use = contracted_use
        results = []
        justCount = []
        daily_highest_concurrent_usage = 0
        hourly_highest_concurrent_usage = 0
        
        while currentDate < end:
            #Find the highest number of used in a 24 hour cycle, by hour
            day = currentDate.strftime(constants.day_fmt)
            if calculation == 'hourly':
                for hour in range(0, 23):
                    count = ReportData.objects.filter(day=day, hour=hour, **filter_args).count()
                    if count > hourly_highest_concurrent_usage:
                        hourly_highest_concurrent_usage = count
                #The highest number is the count
                count = hourly_highest_concurrent_usage
            
            #if the calculation is daily.. we can just count the number of checkins
            elif calculation == 'daily':
                count = ReportDataDaily.objects.filter(day=day, **filter_args).count()
            else:
                _LOG.error('check rules, unsupported format found != hourly,daily')
                raise Exception("unsupported calculation")
            
            #Find the highest count for the given time period
            if count > highest_concurrent_usage:
                highest_concurrent_usage = count
                
            results.append({'date': currentDate.strftime(constants.just_date), 'count': count})
            justCount.append(count)
            currentDate += delta
        
        #return a map of dates, and the count for each date, plus the highest count for the period
        return results, justCount, highest_concurrent_usage
        
        
