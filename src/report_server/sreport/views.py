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
from sreport.models import  ProductUsageForm, ReportData, SpliceServer
from rhic_serve.rhic_rest.models import RHIC, Account
from django.template.response import TemplateResponse
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from common.report import hours_per_consumer

import json

_LOG = logging.getLogger(__name__)

def template_response(request, template_name):
    return render_to_response(template_name, {},
        context_instance=RequestContext(request))

def login(request):
    '''
    login, available at host:port/ui
    '''
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            _LOG.info('successfully authenticated')
            return template_response(request, 'create_report/base.html')
        else:
            _LOG.error('authentication failed')
            return HttpResponseForbidden()
    else:
        _LOG.error('authentication failed, user does not exist')
        return HttpResponseForbidden()

@ensure_csrf_cookie
def logout(request):
    '''
    logout avail at host:port/ui/logout
    '''
    auth_logout(request)
    return template_response(request, 'create_report/logout.html')

@ensure_csrf_cookie
def index(request):
    return template_response(request, 'create_report/base.html')

@login_required
def create_report(request):
    '''
    @param request: http
    '''
    _LOG.info("create_report called by method: %s" % (request.method))
    #ReportFormSet = formset_factory( ProductUsageForm)
    
    contracts = []
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    list_of_contracts = Account.objects.filter(account_id=account)[0].contracts
    list_of_rhics = list(RHIC.objects.filter(account_id=account))
    #environments = [(env, env ) for env in SpliceServer.objects().distinct("environment")]
    environments = SpliceServer.objects.distinct("environment")
    for c in list_of_contracts:
        contracts.append(c.contract_id)
    
    form = ProductUsageForm()
    return render_to_response('create_report/create_report.html', {'form': form, 'contracts': contracts,
                                                                    'account': account, 'user': user, 
                                                                    'list_of_rhics': list_of_rhics,
                                                                    'environments': environments })



def report(request):
    '''
    @param request: http
    
    generate the data for the report.
    data is generated from hours_per_consumer
    
    '''
    _LOG.info("report called by method: %s" % (request.method))
    
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    if 'byMonth' in request.GET:
        month = int(request.GET['byMonth'].encode('ascii'))
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
    if 'rhic' in request.GET:
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
    
    
    
        
    
    response = TemplateResponse(request, 'create_report/report.html',
                                 {'list': results, 'account': account,
                                   'start': start, 'end': end})
    return response


def detailed_report(request):
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    filter_args_dict = json.loads(request.GET['filter_args_dict'])
    start = datetime.fromordinal(int(request.GET['start']))
    end = datetime.fromordinal(int(request.GET['end']))
    
    results = []
    instances = ReportData.objects.filter(date__gt=start, date__lt=end, **filter_args_dict).distinct('instance_identifier')
    for  i in instances:
        count = ReportData.objects.filter(instance_identifier=i, date__gt=start, date__lt=end, **filter_args_dict).count()
        results.append({'instance': i, 'count': count})
    
    this_filter = json.dumps(filter_args_dict)
    response = TemplateResponse(request, 'create_report/details.html', {'list': results, 'account': account,
                                                                        'start': request.GET['start'], 'end': request.GET['end'],
                                                                        'this_filter': this_filter})
    return response

def instance_report(request):
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    instance = request.GET['instance']
    filter_args_dict = json.loads(request.GET['filter_args_dict'])
    start = datetime.fromordinal(int(request.GET['start']))
    end = datetime.fromordinal(int(request.GET['end']))
    
    results = ReportData.objects.filter(instance_identifier=instance, date__gt=start, date__lt=end, **filter_args_dict)
    response = TemplateResponse(request, 'create_report/instance_details.html', {'list': results, 'account': account})
    return response
