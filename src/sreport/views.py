    # Create your views here.
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
        form = ProductUsageForm()
        return render_to_response('create_report/create_report.html', {'form': form})



def report(request):
    #format the data
    consumer_id = request.GET['consumer']
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
    consumer = ConsumerIdentity.objects.get(id = consumer_id)
    uuid = str(consumer)
    
    results = hours_per_consumer(uuid, consumer_id, start, end)
    response = TemplateResponse(request, 'create_report/report.html', {'list': results})
    return response



def get_rhic_uuid(rhic_id):
    
    data = ApiClient.get_all_rhics()
    for rhic in data:
        if rhic.id == rhic_id:
            return rhic.uuid


def hours_per_consumer(my_consumer_uuid, my_consumer_id, start, end):
    results = []
   
    
    
    data = json.loads(ApiClient.get_rhic(my_consumer_id))
    for  contract in data['contracts']:
        for key, value in contract.items():
            if key == 'products':
                for product in value:
                    details = {}
                    details['name'] = product['name']
                    details['engineering_id'] = product['engineering_id']
                    details['sla'] = product['sla']
                    details['support'] = product['support_level']
                    details['contract_use'] = product['quantity']
                    
                    
                    
                    usage_all = ProductUsage.objects.filter(consumer=my_consumer_id)
                    #product_usage = defaultdict(int)
                    counter = 0
                    for i in usage_all:
                        for p in i.product_info:
                            date = p._data['date']
                            product_name = p.product.name
                            product_name_str = str(product_name.encode('ascii'))
                            if product_name_str == details['name']:
                                if start < date < end:
                                    counter += 1
                                else:
                                    print("does not match datetime")
                                
                    details['checkins'] = counter
                        #still need facts from check in service:
                    details['facts'] = 'RAM < 8GB'
                    details['contract_id'] = contract['contract_id']
                    results.append(details)
                    
    return results


    
