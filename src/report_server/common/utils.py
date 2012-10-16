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
from datetime import datetime, timedelta
import logging
import math

_LOG = logging.getLogger(__name__)

def find_item(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item): 
            return item

def datespan_by_hour(startDate, endDate):
    return datespan(startDate, endDate)

def datespan_by_day(startDate, endDate):
    return datespan(startDate, endDate, delta=timedelta(days=1))

def get_datespan(startDate, endDate, product_config):
    if product_config['calculation'] == 'hourly':
        return datespan_by_hour(startDate, endDate)
    if product_config['calculation'] == 'daily':
        return datespan_by_day(startDate, endDate)
        
def datespan(startDate, endDate, delta=timedelta(hours=1)):
    currentDate = startDate
    count = 0
    last_month_days = 0
    hours_for_sub = {}
    total_hours = 0
    while currentDate < endDate:
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
        _LOG.debug(key, value['start'], value['end'], value['hours_for_sub'])
        total_hours += value['hours_for_sub']
    _LOG.debug('total hours:', total_hours)
    return total_hours

def subscription_calc(count, start, end, product_config):
    if product_config['calculation'] == 'hourly':
        hours_for_sub = datespan_by_hour(start, end) 
    if product_config['calculation'] == 'daily':
        hours_for_sub = datespan_by_day(start, end) 
    
    nau = count/hours_for_sub
    nau = math.ceil(nau)
    return nau