# Create your views here.
from __future__ import division
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
from datetime import date, datetime, timedelta
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
import math



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
            return template_response(request, 'create_report/base.html')
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()

@ensure_csrf_cookie
def logout(request):
    auth_logout(request)
    return template_response(request, 'create_report/logout.html')

@ensure_csrf_cookie
def index(request):
    return template_response(request, 'create_report/base.html')

@login_required
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
            return template_response(request, 'create_report/report.html', {'account': account})
    else:
        try:
            contracts = []
            user = str(request.user)
            account = Account.objects.filter(login=user)[0].account_id
            list_of_contracts = Account.objects.filter(account_id=account)[0].contracts
            for c in list_of_contracts:
                contracts.append(c.contract_id)
            
            form = ProductUsageForm()
            return render_to_response('create_report/create_report.html', {'form': form, 'contracts': contracts,
                                                                            'account': account, 'user': user})
        except Exception, e:
            _LOG.exception(e)


def report(request):
    #format the data
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
        
    list_of_rhics = []
    if 'consumer' in request.GET:
        my_uuid = request.GET['consumer']
        list_of_rhics = list(RHIC.objects.filter(uuid=my_uuid))
        results = hours_per_consumer(start, end, list_of_rhics)
        
    elif 'contract_number' in request.GET:
        contract = request.GET['contract_number']
        results = hours_per_consumer(start, end, contract_number=contract)
    
    else:
        rhics = list(RHIC.objects.filter(account_id=account))
        consumer_id = None
        results = hours_per_consumer(start, end, list_of_rhics=rhics)
    
    
    
    response = TemplateResponse(request, 'create_report/report.html', {'list': results, 'account': account, 'start': start, 'end': end})
    return response


def hours_per_consumer(start, end, list_of_rhics=None, contract_number=None):
    results = []
    
    if contract_number:
        list_of_rhics = list(RHIC.objects.filter(contract=contract_number))
        
    for rhic in list_of_rhics:
        account_num = str(RHIC.objects.filter(uuid=str(rhic.uuid))[0].account_id)
        contract_num = str(RHIC.objects.filter(uuid=str(rhic.uuid))[0].contract)
        #list_of_products = Account.objects.filter(account_id=account_num)[0]#.contracts[contract_num].products
        list_of_products = []
            
        contract_list = Account.objects.filter(account_id=account_num)[0].contracts
        for contract in contract_list:
            if contract.contract_id == contract_num:
                list_of_products = contract.products
        
        #list of products in the RHIC's Contract
        for p in list_of_products:
            sub_hours_per_month = datespan(start, end)
            nau_high = 0
            nau_low = 0
            
            for key, value in sub_hours_per_month.items():
                print(key, str(rhic.uuid), p.engineering_id, str(value['start']), str(value['end']), p.sla, p.support_level, str(value['hours_for_sub']))  
                high = ReportData.objects.filter(consumer=str(rhic.uuid), \
                            product=str(p.engineering_id), date__gt=value['start'], \
                            date__lt=value['end'], memtotal__gte=8388608, sla=p.sla, support=p.support_level).count()
                
                low = ReportData.objects.filter(consumer=str(rhic.uuid), \
                            product=str(p.engineering_id), date__gt=value['start'], \
                            date__lt=value['end'], memtotal__lt=8388608, sla=p.sla, support=p.support_level).count()
                if high:
                    nau_high += high / int(value['hours_for_sub'])
                if low:
                    nau_low += low / int(value['hours_for_sub'])
            nau_list =  [nau_high, nau_low]     
            for nau in nau_list:
                if nau:
                    nau = math.ceil(nau)
                    
                    result_dict = {}
                    
                    result_dict['checkins'] = "{0:.0f}".format(nau)
                    result_dict['rhic'] = str(rhic.uuid)
                    result_dict['product_name'] = p.name
                    result_dict['contract_use'] = p.quantity
                    result_dict['sla'] = p.sla
                    result_dict['support'] = p.support_level
                    result_dict['contract_id'] = contract_num
                    
                    
                    if nau_list[0]:  
                        result_dict['facts'] = ' > 8GB  '
                    else:
                        result_dict['facts'] = ' < 8GB  '
                    results.append(result_dict)

    return results


def datespan(startDate, endDate):
    delta=timedelta(hours=1)
    currentDate = startDate
    count = 0
    last_month_days = 0
    hours_for_sub = {}
    while currentDate < endDate:
        hours_for_sub[currentDate.month] = {}
        hours_for_sub[currentDate.month]['start'] = startDate
        if (currentDate + delta).month > currentDate.month :
            sub = count 
            
            hours_for_sub[currentDate.month]['hours_for_sub'] = sub
            hours_for_sub[currentDate.month]['end'] = currentDate
            count = 0
            startDate = currentDate + delta
        
        if currentDate.month == endDate.month:
            last_month_days += 1
            sub = last_month_days 
            hours_for_sub[currentDate.month]['hours_for_sub'] = sub
            hours_for_sub[currentDate.month]['end'] = currentDate
            
        count += 1
        currentDate += delta
        
    return hours_for_sub

def import_checkin_data(request):
    results = []
    #debug
    format = "%a %b %d %H:%M:%S %Y"
    start = datetime.now()
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
    end = datetime.now()
    time['end'] = end.strftime(format)
    results.append(time)
    #debug
    response = TemplateResponse(request, 'test/import.html', {'list': results})
    return response


def detailed_report(request):
    rhic = request.GET['rhic']
    product = request.GET['product']
    start = request.GET['start']
    end = request.GET['end']
    memory = request.GET['memory']
    sla = request.GET['sla']
    support = request.GET['support']
    ReportData.objects.filter(consumer=rhic, \
                            product=product, date__gt=start, \
                            date__lt=end, memtotal__gte=memory, sla=sla, support=support)