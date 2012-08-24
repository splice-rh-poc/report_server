# Create your views here.
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.forms.formsets import formset_factory
from django.shortcuts import render
from django import forms
from django.contrib.auth import (login as auth_login, 
    logout as auth_logout, authenticate)
from django.template import RequestContext
from sreport.models import ConsumerIdentityForm, ProductUsageForm
from sreport.models import ProductUsage, ConsumerIdentity, ReportingItem, MarketingProduct
from django.template.response import TemplateResponse
from django.forms.models import model_to_dict
from kitchen.pycompat25.collections._defaultdict import defaultdict



def template_response(request, template_name):
    return render_to_response(template_name, {},
        context_instance=RequestContext(request))

'''
consumer = ReferenceField(ConsumerIdentity)
    splice_server = ReferenceField(SpliceServer, required=True)
    instance_identifier = StringField(required=True, unique_with=["splice_server", "consumer"]) # example: MAC Address
    product_info = ListField(EmbeddedDocumentField(ReportingItem))
'''

def pulisting(request):
    pu_list = ProductUsage.objects.all()
    final_list = []
    for i in pu_list:
        product_list = []
        mac = i.instance_identifier
        hostname = i.splice_server.hostname
        uuid = i.consumer.uuid
        for p in i.product_info:
            product_list.append(p)
        final_list.append({'mac': mac, 'hostname': hostname, 'uuid': uuid, "products": product_list})
    
    paginator = Paginator(final_list, 1) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        mylist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mylist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mylist = paginator.page(paginator.num_pages)

    return render_to_response('test/list.html', {"list": mylist})

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


    
def create_filter(request):
    #ReportFormSet = formset_factory( ProductUsageForm)
    if request.method == 'POST':
        form = ProductUsageForm(request.POST)
        if form.is_valid():
            #start_date = request.POST['startDate']
            #end_date = request.POST['endDate']
            #splice_server = request.POST['splice_server']
            consumer = request.POST['consumer.value']
            
            results = filtered_results(consumer)
            return template_response(request, 'create_report/machine.html')
    else:
        form = ProductUsageForm()
        return render_to_response('create_report/create.html', {'form': form})

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



def machine_results(request):
    consumer = request.GET['consumer']
    results = filtered_results(consumer)
    response = TemplateResponse(request, 'create_report/list.html', {'list': results})
    return response

def report(request):
    consumer = request.GET['consumer']
    results = hours_per_consumer(consumer)
    response = TemplateResponse(request, 'create_report/report.html', {'list': results})
    return response


def filtered_results(consumer):
    filtered = []
    all =  ProductUsage.objects.all()
    for i in all:
        if str(i.consumer.id) == consumer:
            product_list = []
            consumer_id = i.consumer.id
            mac = i.instance_identifier
            hostname = i.splice_server.hostname
            uuid = i.consumer.uuid
            for p in i.product_info:
                product_list.append(p)
            filtered.append({'mac': mac, 'hostname': hostname, 'uuid': uuid, "products": product_list, 'consumer_id': consumer_id})
    return filtered

def hours_per_consumer(consumer):
    results = []
    all =  ProductUsage.objects.all()
    product_usage = defaultdict(int)
    for i in all:
        
        if str(i.consumer.id) == consumer:
            #product_usage = {}
            
            for p in i.product_info:
                date = p._data['date']
                product_name = p.product.name
                
                product_name_str = str(product_name.encode('ascii'))
                
                product_usage[product_name_str] += 1
        
                    
                
    for key, value in product_usage.items():
        details = {}
        details['name'] = key
        details['checkins'] = value
        details['sla'] = 'Premium'
        details['support'] = 'L1-L3'
        details['facts'] = 'RAM < 8GB'
        details['contract_use'] = '100'
        results.append(details)
    return results
            
        
        
    return results


    
