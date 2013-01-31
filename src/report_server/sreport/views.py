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
from datetime import datetime, timedelta
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.db.models.base import get_absolute_url
from django.db.models.loading import get_model
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth.models import User


from report_server.common import constants, utils
from report_server.common.biz_rules import Rules
from report_server.common.import_util import import_data
from report_server.common.max import MaxUsage
from report_server.common.report import hours_per_consumer
from report_server.common.utils import get_date_epoch, get_date_object
from report_server.sreport.models import ProductUsageForm, ReportData
from report_server.sreport.models import SpliceServer, QuarantinedReportData
from report_server.sreport.models import Account, SpliceAdminGroup, SpliceUserProfile
from rhic_serve.rhic_rest.models import RHIC


import csv
import logging
import json
import sys

_LOG = logging.getLogger(__name__)


def template_response(request, template_name):
    return render_to_response(template_name, {},
                              context_instance=RequestContext(request))


def report(request):
    """
    This is now used by "Export Report" and should be the "GET" equiv
    of report_ui20

    @param request: http

    generate the data for the report.
    data is generated from hours_per_consumer
    
    Returns:
    Content-Disposition:attachment; filename=reportdata.csv
    Content-Type:text/csv

    """
    _LOG.info("report called by method: %s" % (request.method))

    user = str(request.user)
    account = User.objects.filter(username=user)[0].id
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

    if 'env' in request.GET:
        environment = request.GET['env']
    else:
        environment = "All"
        
    

    format = constants.full_format

    response_data = {}
    response_data['list'] = []
    response_data['account'] = account
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response


def ui20(request):
    cookies = request.COOKIES
    for key, value in cookies.items():
        if key == "pxt-session-cookie":
            _LOG.debug('found ' + key + ":" + value)
            user = authenticate(pxt_session=value)
            if user:
                _LOG.debug('user = ' + user.username)
            else:
                _LOG.debug('No user for the session was found')    
    return template_response(request, 'ui20/index.html')


#@ensure_csrf_cookie
def login_ui20(request):
    """
    login, available at host:
    
    Returns:
        {
          "username": "user@host.com", 
          "account": "1190457", 
          "is_admin": true
        }
    """
    """
    cookies = request.COOKIES
    for key, value in cookies.items():
        if key == "pxt-session-cookie":
            _LOG.debug('found ' + key + ":" + value)
            user = authenticate(pxt_session=value)
            if user:
                _LOG.debug('user = ' + user.username)
            else:
                _LOG.debug('No user for the session was found')
    """
    if hasattr(request.session, "_auth_user_id"):
        #ssession = request.session['ssession']
        #user = authenticate(pxt_session=ssession)
        userid = request.session._auth_user_id
        user = User.objects.get(id=userid)
        _LOG.info("ssession: " + request.session["ssession"])
    elif (request.POST.__contains__('username')):
        _LOG.info("no other sessions found")
        username = request.POST['username']
        password = request.POST['password']
        response_data = {}
        user = authenticate(request=request, username=username, password=password)
        if user:
            auth_login(request, user)
        else:
            return HttpResponseForbidden()    
    else:
        _LOG.error('authentication failed, user does not exist')
        logout_ui20(request)
        return HttpResponseForbidden()    
                

    response_data = {}    
    if user is not None:
        #not sure why request.user is not persisting through the middleware
        username = str(request.user)
        print('request.user ' + username)
        _LOG.info('request.user ' + username)
                 
        response_data['is_admin'] = False
        response_data['username'] = username
        if hasattr(user, 'account'):
            response_data['account'] = account.account_id
        else:
            """
            work around for current rhic_serve deployment in the 
            stakeholder env.  The user objects in the stakeholder env do 
            not have the attribute account
            
            """
            setattr(user, 'account', '55555')
            response_data['account'] = user.account
        return HttpResponse(utils.to_json(response_data))
        #else:
        #    _LOG.error('authentication failed')
        #    return HttpResponseForbidden()
    else:
        _LOG.error('authentication failed, user does not exist')
        return HttpResponseForbidden()


@ensure_csrf_cookie
def logout_ui20(request):
    """
    logout avail at host:port/ui/logout
    """
    auth_logout(request)
    return HttpResponse('Worked!')


#@ensure_csrf_cookie
def index_ui20(request):
    """
    index page, setups up UI and javascript calls report_form_ui20
    """
    _LOG.info("index called by method: %s" % (request.method))

    return template_response(request, 'ui20/index.html')


def import_ui20(request):
    """
    The primary method for import should be done via the api
    This is mainly for demo and test purposes atm
    
    Returns:
      {
       "time": [
         {
           "start": "Mon Dec 03 19:55:38 2012", 
           "end": "Mon Dec 03 19:55:58 2012"
         }
       ]
     }
    """
    # response = import_checkin_data(request)
    quarantined, results = import_data()
    response_data = {}
    response_data['time'] = results
    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response


@login_required
def report_form_ui20(request):
    """
    Build the report form. Discovers the associated contracts, rhics and 
    populates the form.
    
    @param request: http
    @param request.user: the currently logged in user
    
    Returns:
       A json doc w/ contracts, user, environment, list_of_rhics
       Example:
       {
        "contracts": [
          "3116649", 
          "3879847"
        ], 
        "user": "user@host.com", 
        "environments": [
          "east"
        ], 
        "list_of_rhics": [
          [
            "8d401b5e-2fa5-4cb6-be64-5f57386fda86", 
            "rhel-server-1190457-3116649-prem-l1-l3"
          ], 
        ]
      }
    """
    # replaces create_report()
    _LOG.info("report_form_ui20 called by method: %s" % (request.method))

    if request.method == 'POST':
        form = ProductUsageForm(request.POST)
        if form.is_valid():
            pass
        else:
            form = ProductUsageForm()

    contracts = []
    user = str(request.user)
    account = '555555'#Account.objects.filter(login=user)[0].account_id
    list_of_contracts = ['0'] #Account.objects.filter(account_id=account)[0].contracts
    list_of_rhics = ['0', '1']#list(RHIC.objects.filter(account_id=account))
    environments = SpliceServer.objects.distinct("environment")
    #for c in list_of_contracts:
    #    contracts.append(c.contract_id)

    # since some item(s) are not json-serializable,
    # extract info we need and pass it along
    # i.e. r.uuid

    response_data = {}
    response_data['contracts'] = contracts
    response_data['user'] = user
    response_data['list_of_rhics'] = list_of_rhics
    response_data['environments'] = environments

    _LOG.info(response_data)

    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response


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
        
    #list_of_rhics = list(RHIC.objects.all())


    # since some item(s) are not json-serializable,
    # extract info we need and pass it along
    # i.e. r.uuid

    response_data = {}
    response_data['list_of_rhics'] = [(str(r.uuid), r.name)
                                      for r in list_of_rhics]

    _LOG.info(response_data)

    try:
        response = HttpResponse(utils.to_json(response_data))
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
    date = datetime.strptime(request.POST['date'], constants.just_date)
    day = date.strftime(constants.day_fmt)

    results = []
    instances = ReportData.objects.filter(
        day=day, **filter_args_dict).distinct('instance_identifier')
    for i in instances:
        count = ReportData.objects.filter(
            instance_identifier=i, day=day, **filter_args_dict).count()
        results.append({'instance': i, 'count': count})

    this_filter = json.dumps(filter_args_dict)

    response_data = {}
    response_data['list'] = results
    response_data['date'] = get_date_epoch(date)
                                            # int(date.strftime("%s")) * 1000
    response_data['this_filter'] = this_filter
    response_data['description'] = description

    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response

@login_required
def report_ui20(request):
    # replaces report(request)
    """
            
    generate the data for the report.
    data is generated from hours_per_consumer
    
    @param request: http
    Args:
        {
            u'byMonth': u'11,2012', (optional)
            u'contract_number': u'All',
            u'env': u'All',
            u'rhic': u'null'
            u'startDate': u'11/01/2012' (optional)
            u'endDate': u'11/30/2012', (optional)
        }

    Returns:
    {
        "start": "Thu Nov 01 00:00:00 2012", 
        "account": "1190457", 
        "end": "Fri Nov 30 00:00:00 2012", 
        "list": [
          [
            {
              "count": 168, 
              "end": 1354251600, 
              "contract_id": "3116649", 
              "contract_use": 20, 
              "support": "l1-l3", 
              "sla": "prem", 
              "start": 1351742400, 
              "compliant": false, 
              "filter_args_dict": "{\"memtotal__gt\": 0, \"product\": [\"69\"],
                \"contract_id\": \"3116649\", \"support\": \"l1-l3\",
                \"memtotal__lt\": 8388608, \"consumer_uuid\":
                \"fea363f5-af37-4a23-a2fd-bea8d1fff9e8\", \"sla\": \"prem\"}", 
              "engineering_id": "[u'69']", 
              "nau": "1", 
              "facts": "< 8GB", 
              "product_config": "{\"calculation\": \"hourly\",
                \"memtotal\": {\"low_gt\": 0, \"low_lt\": 8388608, 
                \"rule\": \"0 > 8388608; 8388608 > 83886080\", 
                \"high_desc\": \"> 8GB\", \"high_gt\": 8388608, 
                \"high_lt\": 83886080, \"low_desc\": \"< 8GB\"}, 
                \"cpu\": [], \"cpu_sockets\": []}", 
              "sub_hours": 696, 
              "product_name": "RHEL Server", 
              "rhic": "rhel-server-jboss-1190457-3116649-prem-l1-l3"
            } 
        ]
      }

    """
    _LOG.info("report called by method: %s" % (request.method))

    user = str(request.user)
    account = User.objects.filter(username=user)[0].id
    try:
        api_data = json.loads(request.raw_post_data)
        data = api_data
    except Exception:
        _LOG.debug('report called, request.raw_post_data does not match expected format')
        try:
            form_data = json.loads(utils.to_json(request.POST))
            data = form_data

        except Exception:
            _LOG.error('report called, request.raw_post_data and '
                       'request.POST do not match expected format')

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

    if 'env' in data:
        environment = data['env']
    else:
        environment = "All"

    
    format = constants.full_format

    response_data = {}
    response_data['list'] = []
    response_data['account'] = account
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response

@login_required
def default_report(request):
    
    _LOG.info("default_report called by method: %s" % (request.method))

    user = str(request.user)
    account = User.objects.filter(username=user)[0].id
    try:
        api_data = json.loads(request.raw_post_data)
        data = api_data
    except Exception:
        _LOG.debug('report called, request.raw_post_data does not match expected format')
        try:
            form_data = json.loads(utils.to_json(request.POST))
            data = form_data

        except Exception:
            _LOG.error('report called, request.raw_post_data and '
                       'request.POST do not match expected format')


    startDate = data['startDate'].split("/")
    endDate = data['endDate'].split("/")
    start = datetime(int(startDate[2]), int(startDate[0]), int(startDate[1]))
    end = datetime(int(endDate[2]), int(endDate[0]), int(endDate[1]))
    environment = data['env']
    """
    #rhic = data['rhic']
    #contract = data['contract_number']
    #list_of_rhics = []
    
 
    list_of_rhics = list(RHIC.objects.filter(account_id=account))
    usuage_compliance = hours_per_consumer(start,
                                 end, 
                                 list_of_rhics=list_of_rhics,
                                 environment=environment,
                                 return_failed_only=True)
    
    fact_compliance = system_fact_compliance_list(account)
    """
    format = constants.full_format

    response_data = {}
    response_data['list'] = []
    response_data['biz_list'] = []
    response_data['account'] = account
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response


def system_fact_compliance(request):
    """
    Search through ReportData.objects and find any objects that do not meet the
    criteria in the business rules as defined in 
    """
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id    
    response_data = {}
    response_data['list'] = system_fact_compliance_list(account)
    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response


def system_fact_compliance_list(account):
    list_of_instances=[]
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
    try:
        response = HttpResponse(utils.to_json(response_data))
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
    date = get_date_object(request.POST['date'])
    day = date.strftime(constants.day_fmt)

    # try:
    #    page = request.POST['page']
    #    page_size = request.POST['page_size']
    # except MultiValueDictKeyError:
    #    page = None
    #    page_size = None
    # except:
    #    _LOG.error(sys.exc_info()[0])
    #    _LOG.error(sys.exc_info()[1])

    # if page is not None and page_size is not None:
    #    left = (request.POST['page'] - 1) * request.POST['page_size']
    #    right = left + request.POST['page_size']
    #    _LOG.info("Fetching instance detail objects [%s:%s]" % (left, right))
    #    results = ReportData.objects[left:right].filter(instance_identifier=instance,
    #                          date__gt=start, date__lt=end, **filter_args_dict)
    # else:
    #    _LOG.info("Fetching all instance detail objects.")
    # results = ReportData.objects.filter(instance_identifier=instance,
    # date__gt=start, date__lt=end, **filter_args_dict)
    results = ReportData.objects.filter(
        instance_identifier=instance, day=day, **filter_args_dict)

    response_data = {}
    response_data['list'] = results
    response_data['account'] = account

    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response


def max_report(request):
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    filter_args_dict = json.loads(request.POST['filter_args_dict'])
    s = request.POST['start']
    e = request.POST['end']
    start = get_date_object(s)
    end = get_date_object(e)
    description = request.POST['description']
    product_name = description.split(',')[0].split(':')[1].strip()

    response_data = MaxUsage.get_MDU_MCU(start, end, filter_args_dict, product_name)
    
    # start.int(date.strftime("%s")) * 1000
    response_data['start'] = get_date_epoch(start) 
    response_data['end'] = get_date_epoch(end)
    response_data['description'] = description
    response_data['filter_args'] = json.dumps(filter_args_dict)

    try:
        # response = HttpResponse(simplejson.dumps(response_data))
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response


def quarantined_report(request):
    # user = str(request.user)
    # account = Account.objects.filter(login=user)[0].account_id
    # filter_args_dict = json.loads(request.POST['filter_args_dict'])
    # s = request.POST['start']
    # e = request.POST['end']
    # start = get_date_object(s)
    # end = get_date_object(e)
    # description = request.POST['description']

    qobjects = []
    qobjects = QuarantinedReportData.objects.all()

    response_data = {}
    response_data['list'] = qobjects
    try:
        response = HttpResponse(utils.to_json(response_data))
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
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(
        ReportData.__name__)
    writer = csv.writer(response)
    # Write headers to CSV file
    headers = []

    # Write data to CSV file
    for f in filter_args_list:
        thismap = json.loads(f)
        # print ReportData.objects.filter(date__gt=start, date__lt=end,
        # **thismap)
        for obj in ReportData.objects.filter(date__gt=start, date__lt=end, **thismap):
            row = [obj.consumer, obj.instance_identifier,
                   obj.product_name, obj.product, obj.hour, obj.splice_server]
            # row.append(getattr(obj), "wes")
            writer.writerow(row)
    # Return CSV file to browser as download
    return response
