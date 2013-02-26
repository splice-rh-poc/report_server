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
from datetime import datetime
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from mongoengine.django.auth import User
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import ensure_csrf_cookie

from report_server.common import constants, utils
from report_server.common.biz_rules import Rules
from report_server.common.import_util import import_data
from report_server.common.max import MaxUsage
from report_server.common.report import hours_per_consumer
from report_server.common.utils import get_date_epoch, get_date_object
from report_server.common.utils import get_dates_from_request, data_from_post, create_response
from report_server.sreport.models import ProductUsageForm, ReportData
from report_server.sreport.models import QuarantinedReportData
from rhic_serve.rhic_rest.models import RHIC, Account


import csv
import logging
import json


_LOG = logging.getLogger(__name__)


def template_response(request, template_name):
    return render_to_response(template_name, {},
                              context_instance=RequestContext(request))


def start_meter(request):
    return template_response(request, 'meter/index.html')


def start_space(request):
    return template_response(request, 'space/index.html')


@ensure_csrf_cookie
def login(request):

    if hasattr(request.session, "_auth_user_id"):
        userid = request.session._auth_user_id
        user = User.objects.get(id=userid)
        _LOG.info("ssession: " + request.session["ssession"])
    elif (request.POST.__contains__('username')):
        _LOG.info("no other sessions found, using credentials")
        username = request.POST['username']
        password = request.POST['password']
        response_data = {}
       
        user = authenticate(request=request, username=username, password=password) 
            
        if not user:
            user = authenticate(username=username, password=password)
            if not user:
                return HttpResponseForbidden() 
        #user found, now authenticate
        auth_login(request, user)
    else:
        _LOG.error('authentication failed, user does not exist')
        logout(request)
        return HttpResponseForbidden()    

    response_data = {}    
    if user is not None:
        username = str(request.user)
        _LOG.info('request.user ' + username)
        response_data['is_admin'] = False
        response_data['username'] = username
        
        if hasattr(user, 'account'):
            response_data['account'] = user.account
        else:
            #in some environments an account number may not be available
            setattr(user, 'account', str(user.id))
            response_data['account'] = user.account
        return HttpResponse(utils.to_json(response_data))
        
    else:
        _LOG.error('authentication failed, user does not exist')
        return HttpResponseForbidden()


@ensure_csrf_cookie
def logout(request):
    """
    logout avail at host:port/ui/logout
    """
    auth_logout(request)
    return HttpResponse('Log out')


@ensure_csrf_cookie
def index(request):
    """
    index page, setups up UI and javascript calls report_form
    """
    _LOG.info("index called by method: %s" % (request.method))

    return template_response(request, 'meter/index.html')


def execute_import(request):
    quarantined, results = import_data()
    response_data = {}
    response_data['time'] = results
    
    return create_response(response_data)


@login_required
def report_form_rhics(request):
    """
    Update the rhic select box based on the selection of the contract

    @param request: http
    """

    _LOG.info("report_form_rhics called by method: %s" % (request.method))

    if request.method == 'POST':
        form = ProductUsageForm(request.POST)
        if form.is_valid():
            pass
        else:
            form = ProductUsageForm()

    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    if request.POST['contract_number'] == "All":
        list_of_rhics = list(RHIC.objects.filter(account_id=account))    
    else:
        contract_number = json.loads(request.POST['contract_number'])
        list_of_rhics = list(RHIC.objects.filter(contract=str(contract_number)))

    response_data = {}
    response_data['list_of_rhics'] = [(str(r.uuid), r.name)
                                      for r in list_of_rhics]

    _LOG.info(response_data)

    return create_response(response_data)


def detailed_report(request):
    filter_args_dict = json.loads(request.POST['filter_args_dict'])
    description = request.POST['description']
    date = datetime.strptime(request.POST['date'], constants.just_date)
    day = date.strftime(constants.day_fmt)

    results = []
    instances = ReportData.objects.filter(day=day, **filter_args_dict).distinct('instance_identifier')
    for i in instances:
        count = ReportData.objects.filter(instance_identifier=i, day=day, **filter_args_dict).count()
        results.append({'instance': i, 'count': count})

    this_filter = json.dumps(filter_args_dict)

    response_data = {}
    response_data['list'] = results
    response_data['date'] = get_date_epoch(date)
    response_data['this_filter'] = this_filter
    response_data['description'] = description

    return create_response(response_data)





@login_required
def default_report(request):
    
    _LOG.info("default_report called by method: %s" % (request.method))

    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    data = data_from_post(request)
    start, end = get_dates_from_request(request)
    environment = data['env']
    list_of_rhics = []
    
    list_of_rhics = list(RHIC.objects.filter(account_id=account))
    args = {'start': start,
            'end': end,
            'list_of_rhics': list_of_rhics,
            'environment': environment,
            'return_failed_only': True
            }
    usuage_compliance = hours_per_consumer(**args)
    
    fact_compliance = system_fact_compliance_list(account)

    format = constants.full_format
    response_data = {}
    response_data['list'] = usuage_compliance
    response_data['biz_list'] = fact_compliance
    response_data['account'] = account
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    return create_response(response_data)


def system_fact_compliance(request):
    """
    Search through ReportData.objects and find any objects that do not meet the
    criteria in the business rules as defined in 
    """
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id    
    response_data = {}
    response_data['list'] = system_fact_compliance_list(account)
    
    return create_response(response_data)


def system_fact_compliance_list(account):
    list_of_instances = []
    rules = Rules()
    report_biz_rules = rules.get_rules()
    list_of_rhics = list(RHIC.objects.filter(account_id=account))
    for rhic in list_of_rhics:
        instances = ReportData.objects.filter(consumer=rhic.name)
        #instances = ReportData.objects.distinct(consumer=rhic.name)
        for i in instances:    
            list_of_instances.append(i.instance_identifier)
    unique_list = set(list_of_instances)
    results = []
    for i in unique_list:
        # we need to find if this instance_identifier has any other products
        # associated w/ it

        products = ReportData.objects.filter(
            instance_identifier=i).distinct('product_name')
        for p in products:
            inst = ReportData.objects.filter(
                instance_identifier=i, product_name=p).first()
            product_rules = report_biz_rules[inst.product_name]
            if product_rules['cpu']:
                if product_rules['cpu']['high_lt'] != -1:
                    if inst.cpu > product_rules['cpu']['high_lt']:
                        results.append([inst, product_rules, 'violates cpu'])
            if product_rules['cpu_sockets']:
                if product_rules['cpu_sockets']['high_lt'] != -1:
                    if inst.cpu_sockets > product_rules['cpu_sockets']['high_lt']:
                        results.append([inst, product_rules, 'violates cpu_sockets'])
            if product_rules['memtotal']:
                if product_rules['memtotal']['high_lt'] != -1:
                    if inst.memtotal > product_rules['memtotal']['high_lt']:
                        results.append([inst, product_rules, 'violates memory'])   
    return results


def unauthorized_pem():
    results = ReportData.objects.filter()

    response_data = {}
    response_data['list'] = results
    return create_response(response_data)


def instance_detail(request):
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    instance = request.POST['instance']
    filter_args_dict = json.loads(request.POST['filter_args_dict'])
    date = get_date_object(request.POST['date'])
    day = date.strftime(constants.day_fmt)

    results = ReportData.objects.filter(
        instance_identifier=instance, day=day, **filter_args_dict)

    response_data = {}
    response_data['list'] = results
    response_data['account'] = account

    return create_response(response_data)


def max_report(request):
    filter_args_dict = json.loads(request.POST['filter_args_dict'])
    s = request.POST['start']
    e = request.POST['end']
    start = get_date_object(s)
    end = get_date_object(e)
    description = request.POST['description']
    product_name = description.split(',')[0].split(':')[1].strip()

    args = {'start': start,
            'end': end,
            'filter_args': filter_args_dict,
            'product_name': product_name
            }
    response_data = MaxUsage.get_MDU_MCU(**args)
    
    response_data['start'] = get_date_epoch(start) 
    response_data['end'] = get_date_epoch(end)
    response_data['description'] = description
    response_data['filter_args'] = json.dumps(filter_args_dict)
    
    return create_response(response_data)
    

def quarantined_report(request):
    qobjects = QuarantinedReportData.objects.all()

    response_data = {}
    response_data['list'] = qobjects
    
    return create_response(response_data)


def export(request):
    if request.method == 'GET':
        result = create_export_report(request)

    mydict = json.loads(result.content)
    list_of_results = mydict['list']
    start = datetime.strptime(mydict['start'], constants.full_format)
    end = datetime.strptime(mydict['end'], constants.full_format)
    filter_args_list = []
    for rhic in list_of_results:
        for products in rhic:
            filter_args_list.append(products['filter_args_dict'])
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(
        ReportData.__name__)
    writer = csv.writer(response)

    # Write data to CSV file
    for f in filter_args_list:
        thismap = json.loads(f)
        # print ReportData.objects.filter(date__gt=start, date__lt=end,
        # **thismap)
        for obj in ReportData.objects.filter(date__gt=start, date__lt=end, **thismap):
            row = [obj.consumer, obj.instance_identifier,
                   obj.product_name, obj.product, obj.hour, obj.splice_server]
            writer.writerow(row)
    # Return CSV file to browser as download
    return response


def create_export_report(request):
    """
    This is now used by "Export Report" and should be the "GET" equiv
    of report

    @param request: http

    generate the data for the report.
    data is generated from hours_per_consumer
    
    Returns:
    Content-Disposition:attachment; filename=reportdata.csv
    Content-Type:text/csv

    """
    _LOG.info("report called by method: %s" % (request.method))

    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    start, end = get_dates_from_request(request)
    
    if 'env' in request.GET:
        environment = request.GET['env']
    else:
        environment = "All"
        
    rhic = request.GET['rhic']
    contract = request.GET['contract_number']    
    list_of_rhics = []
    
    if contract == 'All' and (rhic == 'All' or rhic == 'null'):
        list_of_rhics = list(RHIC.objects.filter(account_id=account))
        results = hours_per_consumer(start,
                                     end, 
                                     list_of_rhics=list_of_rhics,
                                     environment=environment)

    elif rhic != 'null':
        if rhic == "All":
            list_of_rhics = list(RHIC.objects.filter(contract=contract))
        else:
            my_uuid = rhic
            list_of_rhics = list(RHIC.objects.filter(uuid=my_uuid))
        results = hours_per_consumer(start,
                                     end,
                                     list_of_rhics,
                                     environment=environment)

    else:
        list_of_rhics = list(RHIC.objects.filter(account_id=account))
        results = hours_per_consumer(start,
                                     end,
                                     list_of_rhics=list_of_rhics,
                                     environment=environment)

    format = constants.full_format

    response_data = {}
    response_data['list'] = results
    response_data['account'] = account
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    #return create_response(utils.to_json(response_data))
    return create_response(response_data)