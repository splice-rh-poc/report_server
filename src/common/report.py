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

from __future__ import division
import logging


from sreport.models import  ReportData
from rhic_serve.rhic_rest.models import RHIC
from rhic_serve.rhic_rest.models import Account
from datetime import datetime, timedelta
import math
from sets import Set

_LOG = logging.getLogger(__name__)

def hours_per_consumer(start, end, list_of_rhics=None, contract_number=None):
    results = []
    
    if contract_number:
        list_of_rhics = list(RHIC.objects.filter(contract=contract_number))
        
    for rhic in list_of_rhics:
        rhic_list = []
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
            nau_mem_high = 0
            nau_mem_low = 0
            
            for key, value in sub_hours_per_month.items():
                mem_high = ReportData.objects.filter(consumer_uuid=str(rhic.uuid), \
                            product=str(p.engineering_ids), date__gt=value['start'], \
                            date__lt=value['end'], memtotal__gte=8388608, sla=p.sla, support=p.support_level).count()

                mem_low = ReportData.objects.filter(consumer_uuid=str(rhic.uuid), \
                            product=str(p.engineering_ids), date__gt=value['start'], \
                            date__lt=value['end'], memtotal__lt=8388608, sla=p.sla, support=p.support_level).count()
                if mem_high:
                    nau_mem_high += mem_high / int(value['hours_for_sub'])
                    
                    _LOG.debug(str(('found matches w/ the following query', str(key), str(rhic.uuid), 
                            str(p.engineering_ids), 'mem high', str(p.sla), str(p.support_level), str(value['hours_for_sub']))))
                    
                if mem_low:
                    nau_mem_high += mem_high / int(value['hours_for_sub'])
                    nau_mem_low += mem_low / int(value['hours_for_sub'])
                    
                    _LOG.debug(str(('found matches w/ the following query', str(key), str(rhic.uuid), 
                            str(p.engineering_ids), 'mem low', str(p.sla), str(p.support_level), str(value['hours_for_sub']))))
                    
            nau_list =  [nau_mem_high, nau_mem_low]     
            for i, nau in enumerate(nau_list):
                if nau:
                    nau = math.ceil(nau)
                    result_dict = {}
                    
                    
                    result_dict['checkins'] = "{0:.0f}".format(nau)
                    result_dict['rhic'] = str(rhic.name)
                    result_dict['product_name'] = p.name
                    result_dict['engineering_id'] = str(p.engineering_ids)
                    result_dict['contract_use'] = p.quantity
                    result_dict['sla'] = p.sla
                    result_dict['support'] = p.support_level
                    result_dict['contract_id'] = contract_num
                    result_dict['start'] = start.toordinal
                    result_dict['end'] = end.toordinal
                    
                            
                    
                    if i == 0:  
                        result_dict['facts'] = ' > 8GB  '
                        rhic_list.append(result_dict)
                    if i == 1:
                        result_dict['facts'] = ' < 8GB  '
                        rhic_list.append(result_dict)
        if rhic_list:
            results.append(rhic_list)
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


