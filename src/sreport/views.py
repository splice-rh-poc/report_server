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
        consumer_id = request.GET['consumer']
        consumer = ConsumerIdentity.objects.get(id = consumer_id)
        uuid = str(consumer)
        results = hours_per_consumer(start, end, uuid, consumer_id)
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


def hours_per_consumer(start, end, my_consumer_uuid=None, my_consumer_id=None):
    results = []
    if my_consumer_id is not None:
        d = ApiClient.get_rhic(my_consumer_id)[0]
        data = json.loads(d)
    else:
        d = ApiClient.get_contract()[0]
        data = json.loads(d)
        
        list_of_RHICS = ApiClient.getRHIC_in_account()
        
        #unable to get filter to work properly here
        usage_all = []
        for rhic in list_of_RHICS:
            pu = ProductUsage.objects.filter(consumer=rhic)
            if pu:
                usage_all.append(pu)
            
        for pu in usage_all[0]:
            consumer = pu.consumer
        '''
        matching_checkins = []
        total_usage = defaultdict(int)
        for checkin in usage_all:
            myDict = checkin._data
            if checkin.consumer in list_of_RHICS:
                for product in checkin.product_info:
                    usage = {}
                    usage[product] = [checkin.date, checkin.instance_identifier, checkin.splice_server]
                    matching_checkins.append(usage)
        
        for checkin in matching_checkins:
            total_usage = checkin
                    
        '''
    return results


    
