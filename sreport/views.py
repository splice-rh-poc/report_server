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
from datetime import  date, datetime



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
    #format the data
    consumer_id = request.GET['consumer']
    startDate = request.GET['startDate'].encode('ascii').split("/")
    endDate = request.GET['endDate'].encode('ascii').split("/")
    start = datetime(int(startDate[2]), int(startDate[0]), int(startDate[1]))
    end = datetime(int(endDate[2]), int(endDate[0]), int(endDate[1]))
    consumer = ConsumerIdentity.objects.get(id = consumer_id)
    uuid = str(consumer)
    
    results = hours_per_consumer(uuid, consumer_id, start, end)
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

def hours_per_consumer(my_consumer_uuid, my_consumer_id, start, end):
    results = []
    my_consumer = str(my_consumer_uuid).strip()
    buf = cStringIO.StringIO()
    URL = 'http://ec2-184-72-159-16.compute-1.amazonaws.com:8000/api/account/'+ my_consumer + '/'
    USER = 'shadowman@redhat.com'
    PASS = 'shadowman@redhat.com'
    conn = pycurl.Curl()
    conn.setopt(pycurl.USERPWD, "%s:%s" % (USER, PASS))
    conn.setopt(pycurl.URL, URL)
    conn.setopt(pycurl.WRITEFUNCTION, buf.write)
    conn.perform()
    
    
    data = json.loads(buf.getvalue())
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
                    results.append(details)
                    
    return results


    
