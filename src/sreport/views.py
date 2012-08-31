# Create your views here.
import logging

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from django.contrib.auth import (login as auth_login, 
    logout as auth_logout, authenticate)
from django.template import RequestContext
from sreport.models import ProductUsage, ProductUsageForm, ConsumerIdentity
from django.template.response import TemplateResponse
from kitchen.pycompat25.collections._defaultdict import defaultdict
import pycurl, cStringIO, json
from common.client import ApiClient
import datetime


_LOG = logging.getLogger(__name__)

def template_response(request, template_name):
    return render_to_response(template_name, {},
        context_instance=RequestContext(request))

'''
consumer = ReferenceField(ConsumerIdentity)
    splice_server = ReferenceField(SpliceServer, required=True)
    instance_identifier = StringField(required=True, unique_with=["splice_server", "consumer"]) # example: MAC Address
    product_info = ListField(EmbeddedDocumentField(ReportingItem))
'''


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
    return template_response(request, 'base.html')


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
        start = datetime(int(startDate[2]), int(startDate[0]), int(startDate[1]))
        end = datetime(int(endDate[2]), int(endDate[0]), int(endDate[1]))
        
    if 'consumer' in request.GET:
        uuid = request.GET['consumer']
        results = hours_per_consumer(start, end, uuid)
    else:
        consumer_id = None
        results = hours_per_consumer(start, end)
    
    
    
    response = TemplateResponse(request, 'create_report/report.html', {'list': results})
    return response



def get_rhic_uuid(rhic_id):
    
    data = ApiClient.get_all_rhics()
    for rhic in data:
        if rhic.id == rhic_id:
            return rhic.uuid


def hours_per_consumer(start, end, uuid=None):
    results = []
    d = ApiClient.get_contract()[0]
    contract_data = json.loads(d)
        
    list_of_RHICS = ApiClient.getRHIC_in_account()
    
    #unable to get filter to work properly here
    usage_all = []
    
    pu = ProductUsage.objects.filter(consumer=uuid)
    if pu:
        usage_all.append(pu)
    
    total_usage = defaultdict(int)
    for pu in usage_all[0]:
            for product in pu._data['product_info']:
                total_usage[product] += 1
   
    for key, value in total_usage.items():
        result_dict = {}
        result_dict['name'] = key
        result_dict['checkins'] = value
        result_dict['sla'] = 'na'
        result_dict['support'] = 'na'
        result_dict['facts'] = 'na'
        result_dict['contract_id'] = 'na'
        results.append(result_dict)

    return results


    
