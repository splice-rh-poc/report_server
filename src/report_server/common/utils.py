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
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from splice.common import config
import logging
import json
import math
import os
import sys

_LOG = logging.getLogger(__name__)


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
        if (currentDate + delta).month > currentDate.month:
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
        
        if (currentDate + delta).month == 1 and currentDate.month == 12:
            _LOG.debug('plus delta= ' + str((currentDate + delta).month) + ', currentDate = ' + str(currentDate.month))
            sub = count 
            hours_for_sub[currentDate.month]['hours_for_sub'] = sub
            hours_for_sub[currentDate.month]['end'] = currentDate
            count = 0
            startDate = currentDate + delta
            
        count += 1
        currentDate += delta
    
    _LOG.debug(str(hours_for_sub))  
    for key, value in hours_for_sub.items():
        #if 'hours_for_sub' in value:
            #_LOG.debug(str(key) +  str(value['start']) + str(value['end']) +  str(value['hours_for_sub']))
        total_hours += value['hours_for_sub']
    _LOG.debug('total hours: ' + str(total_hours))
    return total_hours


def subscription_calc(count, start, end, product_config):
    if product_config['calculation'] == 'hourly':
        hours_for_sub = datespan_by_hour(start, end) 
    if product_config['calculation'] == 'daily':
        hours_for_sub = datespan_by_day(start, end) 
    
    nau = count / hours_for_sub
    nau = math.ceil(nau)
    return nau


def get_date_epoch(date):
    '''
    return python epoch time * 1000 for javascript 
    '''
    
    epoch = (int(date.strftime("%s")))
    return epoch


def get_date_object(epoch_int):
    '''
    return datetime object from epoch string
    '''
    date = datetime.utcfromtimestamp(int(epoch_int))
    return date


#################################################
# Helper Classes / Methods
#################################################

class MongoEncoder(json.JSONEncoder):
    """ JSON Encoder for Mongo Objects """
    
    def default(self, obj, **kwargs):
        #ObjectId works w/ fedora17 but fails w/ RHEL6
        #from pymongo.objectid import ObjectId
        import mongoengine
        import types
        if isinstance(obj, (mongoengine.Document, mongoengine.EmbeddedDocument)):
            out = dict(obj._data)
            for k,v in out.items():
                #if isinstance(v, ObjectId):
                _LOG.debug("k = %s, v = %s" % (k,v))
                out[k] = str(v)
            return out
        elif isinstance(obj, mongoengine.queryset.QuerySet):
            return list(obj)
        elif isinstance(obj, types.ModuleType):
            return None
        elif isinstance(obj, (list, dict)):
            return obj
        elif isinstance(obj, datetime):
            return str(obj)
        else:
            msg = ('object type not found, can not encode to JSON')
            _LOG.error(msg)
            raise Exception(msg)
    

def to_json(obj):
    return json.dumps(obj, cls=MongoEncoder, indent=2)


def read_rhn_conf():
    config_file = '/etc/rhn/rhn.conf'
    config_section = 'spacewalk'
    rhn_dict = {}
    keys = ['db_backend', 'db_user', 'db_password', 'db_name', 'db_host', 'db_port']
    if os.path.isfile(config_file):
        if not config.CONFIG.has_section(config_section):
            config.CONFIG.add_section(config_section)
        _LOG.info('found ' + config_file)
        file = open(config_file, 'r')
        for line in file:
            for key in keys:
                if key in line:
                    _LOG.debug(line)
                    value = line.split('=')[1].strip()
                    rhn_dict[key] = value
    for key, value in rhn_dict.items():
        #_LOG.info(str(key) + ':' + str(value))
        config.CONFIG.set(config_section, key, value)
                    
            

def get_dates_from_request(request):
    start = None
    end = None
    if not request.POST: 
        if 'byMonth' in request.GET:
                month_year = request.GET['byMonth'].encode('ascii').split('%2C')
                month = int(month_year[0])
                year = int(month_year[1])
                start = datetime(year, month, 1)
                if month == 12:
                    end = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end = datetime(year, month + 1, 1) - timedelta(days=1)
        else:
    
            startDate = request.GET['startDate'].encode('ascii').split("%2F")
            endDate = request.GET['endDate'].encode('ascii').split("%2F")
            start = datetime(
                int(startDate[2]), int(startDate[0]), int(startDate[1]))
            end = datetime(int(endDate[2]), int(endDate[0]), int(endDate[1]))
            
    else:
        data = data_from_post(request)
        if 'byMonth' in data:
                month_year = data['byMonth'].split(',')
                month = int(month_year[0])
                year = int(month_year[1])
                #year = datetime.today().year
                start = datetime(year, month, 1)
                if month == 12:
                    end = datetime((year + 1), 1, 1) - timedelta(days=1)
                else:
                    end = datetime(year, month + 1, 1) - timedelta(days=1)
        if 'startDate' in data:
            startDate = data['startDate'].split("/")
            endDate = data['endDate'].split("/")
            start = datetime(
                int(startDate[2]), int(startDate[0]), int(startDate[1]))
            end = datetime(int(endDate[2]), int(endDate[0]), int(endDate[1]))        
        
    
    return start, end


def data_from_post(request):
    data = None
    try:
        api_data = json.loads(request.raw_post_data)
        data = api_data
    except Exception:
        _LOG.debug('report called, request.raw_post_data does not match expected format')
        try:
            form_data = json.loads(to_json(request.POST))
            data = form_data

        except Exception as e:
            _LOG.critical('report called, request.raw_post_data and '
                       'request.POST do not match expected format')
            return HttpResponseServerError
    return data


def create_response(response_data):
    try:
        response = HttpResponse(to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise
    return response
    
        