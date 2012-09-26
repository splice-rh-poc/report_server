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
from sreport.models import  ReportData
import math
import logging
from utils import datespan
import json



_LOG = logging.getLogger(__name__)

class Product_Def:

    @staticmethod
    def get_product_match(product, rhic, start, end, contract_number):
        
        count_list = []
        
        if (product.name == "RHEL Server") or \
             (product.name ==  "RHEL HA") or  \
               (product.name ==  "RHEL EUS") or \
                 (product.name ==  "RHEL Server for Education") or \
                   (product.name ==  "RHEL LB"):
            #print(RHEL_Server_High(product, rhic, start, end))
            count, filter_args_dict = RHEL_Server_High(product, rhic, start, end)
            if(count):
                result_dict = build_result(product, rhic, start, end, contract_number, count)
                result_dict['facts'] = ' > 8GB  '
                result_dict['filter_args_dict']=json.dumps(filter_args_dict)
                count_list.append(result_dict)
            
            #print(RHEL_Server_Low(product, rhic, start, end))
            count, filter_args_dict = RHEL_Server_Low(product, rhic, start, end)
            if(count):
                result_dict = build_result(product, rhic, start, end, contract_number, count)
                result_dict['facts'] = ' < 8GB  '
                result_dict['filter_args_dict']=json.dumps(filter_args_dict)
                count_list.append(result_dict)
            
            return count_list
        elif product.name == "JBoss EAP":
            count, filter_args_dict = JBoss_EAP_VCPU_gt4(product, rhic, start, end)
            if(count):
                result_dict = build_result(product, rhic, start, end, contract_number, count)
                result_dict['facts'] = ' > 4 vCPU  '
                result_dict['filter_args_dict']=json.dumps(filter_args_dict)
                count_list.append(result_dict)
                
            count, filter_args_dict = JBoss_EAP_VCPU_lt4(product, rhic, start, end)
            if(count):
                result_dict = build_result(product, rhic, start, end, contract_number, count)
                result_dict['facts'] = ' < 4 vCPU  '
                result_dict['filter_args_dict']=json.dumps(filter_args_dict)
                count_list.append(result_dict)
                
            return count_list
        
        elif product.name == "RHEL Server 2-socket Unlimited Guest":
            _LOG.error('not supported') # need more info
            
        elif product.name == "OpenShift Gear":
            count, filter_args_dict = OpenShift_Gear_high(product, rhic, start, end)
            if(count):
                result_dict = build_result(product, rhic, start, end, contract_number, count)
                result_dict['facts'] = ' > 1 vCPU, > 2GB  '
                result_dict['filter_args_dict']=filter_args_dict
                count_list.append(result_dict)
            
            count, filter_args_dict = OpenShift_Gear_low(product, rhic, start, end)
            if(count):
                result_dict = build_result(product, rhic, start, end, contract_number, count)
                result_dict['facts'] = '  1 vCPU, <= 2GB  '
                result_dict['filter_args_dict']=filter_args_dict
                count_list.append(result_dict)
            return count_list
        
         

def build_result(product, rhic, start, end, contract_number, count):
    result_dict = {}
    hours_for_sub = datespan(start, end) 
    nau = count / int(hours_for_sub)
    nau = math.ceil(nau)
    
    
    result_dict['checkins'] = "{0:.0f}".format(nau)
    result_dict['rhic'] = str(rhic.name)
    result_dict['product_name'] = product.name
    result_dict['engineering_id'] = str(product.engineering_ids)
    result_dict['contract_use'] = product.quantity
    result_dict['sla'] = product.sla
    result_dict['support'] = product.support_level
    result_dict['contract_id'] = contract_number
    result_dict['start'] = start.toordinal
    result_dict['end'] = end.toordinal
    
    return result_dict
    
    
def RHEL_Server_High(product, rhic, start, end):
    filter_args_dict={ 'consumer_uuid': str(rhic.uuid), \
                      'product': product.engineering_ids, 'memtotal__gte': 8388608, \
                      'sla': product.sla, 'support': product.support_level}
        
    mem_high = ReportData.objects.filter(date__gt=start, date__lt=end, **filter_args_dict).count()
                                
    return mem_high, filter_args_dict
    
    
def RHEL_Server_Low(product, rhic, start, end):
    filter_args_dict={ 'consumer_uuid': str(rhic.uuid), \
                      'product': product.engineering_ids, 'memtotal__lte': 8388608, \
                      'sla': product.sla, 'support': product.support_level}
    
    mem_low = ReportData.objects.filter(date__gt=start, date__lt=end, **filter_args_dict).count()
                            
    return mem_low, filter_args_dict
    
    
def JBoss_EAP_VCPU_gt4(product, rhic, start, end):
    filter_args_dict={ 'consumer_uuid': str(rhic.uuid), \
                      'product': product.engineering_ids, 'cpu_sockets__gte': 4, \
                      'sla': product.sla, 'support': product.support_level}
    
    jboss_high = ReportData.objects.filter(date__gt=start, date__lt=end, **filter_args_dict).count()
                            
    return jboss_high, filter_args_dict

def JBoss_EAP_VCPU_lt4(product, rhic, start, end):
    filter_args_dict={ 'consumer_uuid': str(rhic.uuid), \
                      'product': product.engineering_ids, 'cpu_sockets__lt': 4, \
                      'sla': product.sla, 'support': product.support_level}
    
    jboss_high = ReportData.objects.filter(date__gt=start, date__lt=end, **filter_args_dict).count()
                            
    return jboss_high, filter_args_dict
    
def OpenShift_Gear_high(product, rhic, start, end):
    filter_args_dict={ 'consumer_uuid': str(rhic.uuid), \
                      'product': product.engineering_ids,  \
                      'cpu_sockets__gte': 4, 'memtotal__gte': 8388608, \
                      'sla': product.sla, 'support': product.support_level}
    
    high = ReportData.objects.filter(date__gt=start, date__lt=end, **filter_args_dict).count()
                            
    return high, filter_args_dict
    
def OpenShift_Gear_low(product, rhic, start, end):
    filter_args_dict={ 'consumer_uuid': str(rhic.uuid), \
                      'product': product.engineering_ids,  \
                       'cpu_sockets__lt': 4, 'memtotal__lt': 8388608, \
                       'sla': product.sla, 'support': product.support_level}
    
    low = ReportData.objects.filter(date__gt=start, date__lt=end, **filter_args_dict).count()
                            
    return low, filter_args_dict