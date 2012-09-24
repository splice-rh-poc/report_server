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

import math
from sets import Set
from products import Product_Def


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
            nau_mem_high = 0
            nau_mem_low = 0
            _LOG.debug(p.name)
            print(p.name)
            results_dicts = []
            results_dicts = Product_Def.get_product_match(p, rhic, start, end, contract_num)
            
            if results_dicts:
                for result in results_dicts:
                    rhic_list.append(result)
        if rhic_list:
            results.append(rhic_list)
    return results




