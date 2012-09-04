# Create your views here.
import logging
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from django.contrib.auth import (login as auth_login, 
    logout as auth_logout, authenticate)
from django.template import RequestContext
from sreport.models import ProductUsage, ProductUsageForm
from django.template.response import TemplateResponse
from kitchen.pycompat25.collections._defaultdict import defaultdict
from common.client import ApiClient
import datetime


_LOG = logging.getLogger(__name__)

def template_response(request, template_name):
    return render_to_response(template_name, {},
        context_instance=RequestContext(request))

def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return template_response(request, 'create_report/create_report.html')
        else:
            pass
            # Return a 'disabled account' error message
    else:
        pass
        # Return an 'invalid login' error message.    

def logout(request):
    auth_logout(request)
    return template_response(request, 'logout.html')

def index(request):
    return template_response(request, 'create_report/base.html')


def create_report(request):
    _LOG.info("create_report called by method: %s" % (request.method))
    #ReportFormSet = formset_factory( ProductUsageForm)
    if request.method == 'POST':
        form = ProductUsageForm(request.POST)
        if form.is_valid():
            #start_date = request.POST['startDate']
            #end_date = request.POST['endDate']
            #splice_server = request.POST['splice_server']
            consumer = request.POST['consumer.value']
            
            results = hours_per_consumer(consumer)
            return template_response(request, 'create_report/report.html')
    else:
        try:
            form = ProductUsageForm()
            return render_to_response('create_report/create_report.html', {'form': form})
        except Exception, e:
            _LOG.exception(e)


def report(request):
    #format the data
    
        
    if 'viaMonth' in request.GET:
        month = int(request.GET['viaMonth'].encode('ascii'))
        year = datetime.datetime.today().year
        start = datetime.datetime(year, month, 1)
        end =  datetime.datetime(year, month + 1, 1) - datetime.timedelta (days = 1)
    else:
        
        startDate = request.GET['startDate'].encode('ascii').split("/")
        endDate = request.GET['endDate'].encode('ascii').split("/")
        start = datetime.datetime(int(startDate[2]), int(startDate[0]), int(startDate[1]))
        end = datetime.datetime(int(endDate[2]), int(endDate[0]), int(endDate[1]))
        
    if 'consumer' in request.GET:
        uuid = request.GET['consumer']
        results = hours_per_consumer(start, end, uuid)
    else:
        consumer_id = None
        results = hours_per_consumer(start, end)
    
    
    
    response = TemplateResponse(request, 'create_report/report.html', {'list': results})
    return response



def hours_per_consumer(start, end, uuid=None):
    results = []
    account_data = ApiClient.get_account()
    
        
    
    #unable to get filter to work properly here
    usage_all = []
    
    # PER RHIC UUID
    rhic_data = ApiClient.get_rhic_details(uuid)
    if not rhic_data:
        return results
    
    contract_number = rhic_data['contract']
    contract_api = ""
    for i in account_data:
        print(i)
        for contracts in i['contracts']:
            if contracts['contract_id'] == contract_number:
                contract_uri = contracts['resource_uri'].encode('ascii')
                contract_uri = contract_uri.split('/')[3:]
                for i in contract_uri:
                    contract_api += "/" + i
    # Contract Data is currently broken due to tasty pie
    #contract_data = ApiClient.get_contract(contract_api)
    #contract_data = json.loads(contract_data)
    #print(contract_data)
    
    pu = ProductUsage.objects.filter(consumer=uuid)
    if pu:
        usage_all.append(pu)
    
    
    total_usage = defaultdict(int)
    for pu in usage_all[0]:
        for product in pu._data['product_info']:
            if start < pu._data['date'] < end: 
                total_usage[product] += 1

    for key, value in total_usage.items():
        result_dict = {}
        #for products in contract_data:
        #for products in total_usage:
        #if products['engineering_id'] == key:
         #  result_dict['name'] = products['name']
        result_dict['name'] = key
        result_dict['checkins'] = value
        result_dict['contract_use'] = 0 #products['quantity']
        result_dict['sla'] = rhic_data['sla']
        result_dict['support'] = rhic_data['support_level']
        result_dict['facts'] = 0 #pu._data['facts']
        result_dict['contract_id'] = rhic_data['contract']
        results.append(result_dict)

    return results


    
