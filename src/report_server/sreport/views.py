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

# Create your views here.
from __future__ import division
import logging
from django.shortcuts import render_to_response
from django.contrib.auth import (login as auth_login, 
    logout as auth_logout, authenticate)

from django.template import RequestContext
from report_server.sreport.models import  ProductUsageForm, ReportData, SpliceServer
from rhic_serve.rhic_rest.models import RHIC, Account
from django.template.response import TemplateResponse
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from report_server.common.report import hours_per_consumer
from report_server.common.import_util import import_data
import sys
from django.http import HttpResponse
from report_server.common import constants
from report_server.common.max import MaxUsage
import json
from django.db.models.base import get_absolute_url
from django.utils.datastructures import MultiValueDictKeyError
import csv
from django.template.defaultfilters import slugify
from django.db.models.loading import get_model



_LOG = logging.getLogger(__name__)

def template_response(request, template_name):
    return render_to_response(template_name, {},
        context_instance=RequestContext(request))




def report(request):
    '''
    This is now used by "Export Report" and should be the "GET" equiv
    of report_ui20
    
    @param request: http
    
    generate the data for the report.
    data is generated from hours_per_consumer
    
    '''
    _LOG.info("report called by method: %s" % (request.method))
    
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    if 'byMonth' in request.GET:
        month_year = request.GET['byMonth'].encode('ascii').split('%2C')
        month = int(month_year[0]);
        year = int(month_year[1]);
        year = datetime.today().year
        start = datetime(year, month, 1)
        end =  datetime(year, month + 1, 1) - timedelta (days = 1)
    else:
        
        startDate = request.GET['startDate'].encode('ascii').split("/")
        endDate = request.GET['endDate'].encode('ascii').split("/")
        start = datetime(int(startDate[2]), int(startDate[0]), int(startDate[1]))
        end = datetime(int(endDate[2]), int(endDate[0]), int(endDate[1]))
    
    if 'env' in request.GET:
        environment = request.GET['env']
    else:
        environment = "All"
        
    list_of_rhics = []
    if request.GET['rhic'] != 'null':
        my_uuid = request.GET['rhic']
        list_of_rhics = list(RHIC.objects.filter(uuid=my_uuid))
        results = hours_per_consumer(start, end, list_of_rhics, environment=environment)
        
    elif 'contract_number' in request.GET:
        contract = request.GET['contract_number']
        if contract == "All":
            list_of_rhics = list(RHIC.objects.filter(account_id=account))
            results = hours_per_consumer(start, end, list_of_rhics=list_of_rhics, environment=environment)
        else:
            results = hours_per_consumer(start, end, contract_number=contract, environment=environment)
    
    else:
        list_of_rhics = list(RHIC.objects.filter(account_id=account))
        results = hours_per_consumer(start, end, list_of_rhics=list_of_rhics, environment=environment)
    
    format = constants.full_format

    response_data = {}
    response_data['list'] = results
    response_data['account'] = account
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    try:
        response = HttpResponse(to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response





#################################################
# Helper Classes / Methods
#################################################

class MongoEncoder(json.JSONEncoder):
    """ JSON Encoder for Mongo Objects """
    def default(self, obj, **kwargs):
        from pymongo.objectid import ObjectId
        import mongoengine
        import types
        if isinstance(obj, (mongoengine.Document, mongoengine.EmbeddedDocument)):
            out = dict(obj._data)
            for k,v in out.items():
                if isinstance(v, ObjectId):
                    _LOG.info("k = %s, v = %s" % (k,v))
                    out[k] = str(v)
            return out
        elif isinstance(obj, mongoengine.queryset.QuerySet):
            return list(obj)
        elif isinstance(obj, types.ModuleType):
            return None
        elif isinstance(obj, (list,dict)):
            return obj
        elif isinstance(obj, datetime):
            return str(obj)
        else:
            return JSONEncoder.default(obj, **kwargs)

def to_json(obj):
    return json.dumps(obj, cls=MongoEncoder, indent=2)


#################################################
# UI 2.0 Contents
#################################################

def ui20(request):
    return template_response(request, 'ui20/index.html')

@ensure_csrf_cookie
def login_ui20(request):
    '''
    login, available at host:port/ui/ui20
    '''
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            _LOG.info('successfully authenticated')
            username = str(request.user)
            account = Account.objects.filter(login=username)[0].account_id
            #the User object/model needs to be modified to allow 
            #for more attributes like account
            #This would accommodate template usage {{ user.account }} in css
            #The following return of username/account should eventually be removed
            return HttpResponse(username + ' ' + account)
        else:
            _LOG.error('authentication failed')
            return HttpResponseForbidden()
    else:
        _LOG.error('authentication failed, user does not exist')
        return HttpResponseForbidden()

@ensure_csrf_cookie
def logout_ui20 (request):
    '''
    logout avail at host:port/ui/logout
    '''
    auth_logout(request)
    return HttpResponse('Worked!')

@ensure_csrf_cookie
def index_ui20(request):
    _LOG.info("index called by method: %s" % (request.method))

    return template_response(request, 'ui20/index.html')

def import_ui20(request):
    #response = import_checkin_data(request)
    results = import_data()
    response_data = {}
    response_data['time'] = results
    try:
        response = HttpResponse(to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response

@login_required
def report_form_ui20(request):
    #replaces create_report()
    _LOG.info("report_form_ui20 called by method: %s" % (request.method))
   
    if request.method == 'POST':
        form = ProductUsageForm(request.POST)
        if form.is_valid():
            pass
        else: 
            form = ProductUsageForm()
    
    contracts = []
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    list_of_contracts = Account.objects.filter(account_id=account)[0].contracts
    list_of_rhics = list(RHIC.objects.filter(account_id=account))
    environments = SpliceServer.objects.distinct("environment")
    for c in list_of_contracts:
        contracts.append(c.contract_id)

    # since some item(s) are not json-serializable, 
    # extract info we need and pass it along
    # i.e. r.uuid

    response_data = {}
    response_data['contracts'] = contracts
    response_data['user'] = user
    response_data['list_of_rhics'] = [(str(r.uuid), r.name) for r in list_of_rhics]
    response_data['environments'] = environments

    _LOG.info(response_data)
    
    try:
        response = HttpResponse(to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response

def report_ui20(request):
    #replaces report(request)
    '''
    @param request: http
    
    generate the data for the report.
    data is generated from hours_per_consumer
    
    '''
    _LOG.info("report called by method: %s" % (request.method))
    
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    if 'byMonth' in request.POST:
        month_year = request.POST['byMonth'].encode('ascii').split(',')
        month = int(month_year[0]);
        year = int(month_year[1]);
        year = datetime.today().year
        start = datetime(year, month, 1)
        end =  datetime(year, month + 1, 1) - timedelta (days = 1)
    else:
        startDate = request.POST['startDate'].encode('ascii').split("/")
        endDate = request.POST['endDate'].encode('ascii').split("/")
        start = datetime(int(startDate[2]), int(startDate[0]), int(startDate[1]))
        end = datetime(int(endDate[2]), int(endDate[0]), int(endDate[1]))
    
    if 'env' in request.POST:
        environment = request.POST['env']
    else:
        environment = "All"
        
    list_of_rhics = []
    if request.POST['rhic'] != 'null':
        my_uuid = request.POST['rhic']
        list_of_rhics = list(RHIC.objects.filter(uuid=my_uuid))
        results = hours_per_consumer(start, end, list_of_rhics, environment=environment)
        
    elif request.POST['contract_number'] != 'null':
        contract = request.POST['contract_number']
        if contract == "All":
            list_of_rhics = list(RHIC.objects.filter(account_id=account))
            results = hours_per_consumer(start, end, list_of_rhics=list_of_rhics, environment=environment)
        else:
            results = hours_per_consumer(start, end, contract_number=contract, environment=environment)
    
    else:
        list_of_rhics = list(RHIC.objects.filter(account_id=account))
        results = hours_per_consumer(start, end, list_of_rhics=list_of_rhics, environment=environment)
    
    format = constants.full_format

    response_data = {}
    response_data['list'] = results
    response_data['account'] = account
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    try:
        response = HttpResponse(to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response

def detailed_report_ui20(request):
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    filter_args_dict = json.loads(request.POST['filter_args_dict'])
    description = request.POST['description']
    start = datetime.fromordinal(int(request.POST['start']))
    end = datetime.fromordinal(int(request.POST['end']))
    
    results = []
    instances = ReportData.objects.filter(date__gt=start, date__lt=end, **filter_args_dict).distinct('instance_identifier')
    for i in instances:
        count = ReportData.objects.filter(instance_identifier=i, date__gt=start, date__lt=end, **filter_args_dict).count()
        results.append({'instance': i, 'count': count})
    
    this_filter = json.dumps(filter_args_dict)

    response_data = {}
    response_data['list'] = results
    response_data['start'] = start.toordinal()
    response_data['end'] = end.toordinal()
    response_data['this_filter'] = this_filter
    response_data['description'] = description


    try:
        response = HttpResponse(to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response

def instance_detail_ui20(request):
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    instance = request.POST['instance']
    filter_args_dict = json.loads(request.POST['filter_args_dict'])
    start = datetime.fromordinal(int(request.POST['start']))
    end = datetime.fromordinal(int(request.POST['end']))
    #try:
    #    page = request.POST['page']
    #    page_size = request.POST['page_size']
    #except MultiValueDictKeyError:
    #    page = None
    #    page_size = None
    #except:
    #    _LOG.error(sys.exc_info()[0])
    #    _LOG.error(sys.exc_info()[1])

    #if page is not None and page_size is not None:
    #    left = (request.POST['page'] - 1) * request.POST['page_size']
    #    right = left + request.POST['page_size']
    #    _LOG.info("Fetching instance detail objects [%s:%s]" % (left, right))
    #    results = ReportData.objects[left:right].filter(instance_identifier=instance, date__gt=start, date__lt=end, **filter_args_dict)
    #else:
    #    _LOG.info("Fetching all instance detail objects.")
    #    results = ReportData.objects.filter(instance_identifier=instance, date__gt=start, date__lt=end, **filter_args_dict)
    results = ReportData.objects.filter(instance_identifier=instance, date__gt=start, date__lt=end, **filter_args_dict)

    response_data = {}
    response_data['list'] = results
    response_data['account'] = account

    try:
        response = HttpResponse(to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response

def max_report(request):
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    filter_args_dict = json.loads(request.POST['filter_args_dict'])
    start = datetime.fromordinal(int(request.POST['start']))
    end = datetime.fromordinal(int(request.POST['end']))
    description = request.POST['description']
    product_name = description.split(',')[0].split(':')[1].strip()
    
    
    results, mdu, mcu, daily_contract, date = MaxUsage.get_MDU_MCU(start, end,  filter_args_dict, product_name)
    

    
    response_data = {}
    response_data['list'] = results
    response_data['start'] = start.toordinal()
    response_data['end'] = end.toordinal()
    response_data['mdu'] = mdu
    response_data['mcu'] = mcu
    response_data['date'] = date
    response_data['description'] = description
    response_data['daily_contract'] = daily_contract

    try:
        #response = HttpResponse(simplejson.dumps(response_data))
        response = HttpResponse(to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response

def export(request):
    if request.method == 'GET':
        result = report(request)
    
    mydict = json.loads(result.content)
    list_of_results = mydict['list']
    start = datetime.strptime(mydict['start'], constants.full_format)
    end = datetime.strptime(mydict['end'], constants.full_format)
    filter_args_list = []
    for rhic in list_of_results:
        for products in rhic:
            filter_args_list.append(products['filter_args_dict'])
    
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(ReportData.__name__)
    writer = csv.writer(response)
    # Write headers to CSV file
    headers = []
    
    # Write data to CSV file
    for f in filter_args_list:
        thismap = json.loads(f)
        #print ReportData.objects.filter(date__gt=start, date__lt=end, **thismap)
        for obj in ReportData.objects.filter(date__gt=start, date__lt=end, **thismap):
            row = [obj.consumer, obj.instance_identifier, obj.product_name, obj.product, obj.hour, obj.splice_server]
            #row.append(getattr(obj), "wes")
            writer.writerow(row)
    # Return CSV file to browser as download
    return response
    

