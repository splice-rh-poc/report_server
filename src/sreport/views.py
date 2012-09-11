# Create your views here.
import logging
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from django.contrib.auth import (login as auth_login, 
    logout as auth_logout, authenticate)
from django.template import RequestContext
from sreport.models import ProductUsage, ProductUsageForm, ReportData, RHIC, Account
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
        my_uuid = request.GET['consumer']
        results = hours_per_consumer(start, end, my_uuid)
    else:
        consumer_id = None
        results = hours_per_consumer(start, end)
    
    
    
    response = TemplateResponse(request, 'create_report/report.html', {'list': results})
    return response


def hours_per_consumer(start, end, my_uuid=None):
    results = []
    pu_all = list(ReportData.objects.filter(consumer=my_uuid))
    total_usage = defaultdict(int)
    '''
    for pu in pu_all:
        for product in pu.product_info:
            if start < pu.date < end: 
                total_usage[product] += 1
    '''
    list_of_products = ReportData.objects.distinct('product')
    for prod in list_of_products:
        pu_product = list(ReportData.objects.filter(consumer=my_uuid, product=prod, date__gt=start, date__lt=end))
        
                
        result_dict = {}
        if pu_product:
            product = pu_product[0]
    
            result_dict['product_name'] = product.product_name
            result_dict['checkins'] = len(pu_product)
            result_dict['contract_use'] = product.contract_use
            result_dict['sla'] = product.sla
            result_dict['support'] = product.support
            result_dict['facts'] = 'total memory: ' + str(product.memtotal)
            result_dict['contract_id'] = product.contract_id
            results.append(result_dict)
    return results

def import_checkin_data(request):
    results = []
    #debug
    format = "%a %b %d %H:%M:%S %Y"
    start = datetime.datetime.now()
    time = {}
    time['start'] = start.strftime(format)
    #debug
    
    hr_fmt = "%m%d%Y:%H"
    pu_all = list(ProductUsage.objects.all())
    for pu in pu_all:
        #my_uuid = pu._data['consumer']
        my_uuid = str(pu.consumer)
        try:
            this_rhic = RHIC.objects.filter(uuid=my_uuid)[0]
        except IndexError:
            #print(pu)
            pass
        this_account = Account.objects.filter(account_id=this_rhic.account_id)[0]
        
        my_products = []
        for c in  this_account.contracts:
            if c.contract_id == this_rhic.contract:
                        my_products = c.products
                        
                            
        
        
        total_usage = defaultdict(int)
            #for product_pem in pu._data['product_info']:
        for product_pem in pu.product_info:
            for p in my_products:
                if int(product_pem) == int(p.engineering_id):
                    this_product = p
                    print(str(pu.instance_identifier + ' ' + str(pu.date)))
                    try:
                        mem = pu.facts['memory_dot_memtotal']
                    except:
                        mem = 0
                    rd = ReportData(instance_identifier=str(pu.instance_identifier), 
                                    consumer = str(pu.consumer),
                                    product = str(this_product.engineering_id),
                                    product_name = this_product.name,
                                    date = pu.date,
                                    hour = pu.date.strftime(hr_fmt),
                                    sla = this_product.sla,
                                    support = this_product.support_level,
                                    contract_id = str(this_rhic.contract),
                                    contract_use = str(this_product.quantity),
                                    memtotal = int(mem)
                                    
                                    )
                    dupe = ReportData.objects.filter(instance_identifier=str(pu.instance_identifier), hour=pu.date.strftime(hr_fmt), product=str(this_product.engineering_id))
                    if dupe:
                        print("found dupe:" + str(pu))
                    else:
                        rd.save()
    
    #debug
    end = datetime.datetime.now()
    time['end'] = end.strftime(format)
    results.append(time)
    #debug
    response = TemplateResponse(request, 'test/import.html', {'list': results})
    return response
