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
from sreport.models import ProductUsage, ReportData
from rhic_serve.rhic_rcs.models import RHIC
from rhic_serve.rhic_rest.models import Account
from datetime import datetime
from common.utils import find_item
from sets import Set

_LOG = logging.getLogger(__name__)

def checkin_data():
    results = []
    #debug
    format = "%a %b %d %H:%M:%S %Y"
    start = datetime.utcnow()
    time = {}
    time['start'] = start.strftime(format)
    #debug
    
    hr_fmt = "%m%d%Y:%H"
    pu_all = ProductUsage.objects.all()
    for pu in pu_all:
        #my_uuid = pu._data['consumer']
        my_uuid = str(pu.consumer)
        try:
            this_rhic = RHIC.objects.filter(uuid=my_uuid)[0]
        except IndexError:
            _LOG.critical('rhic not found @ import')
            raise Exception('rhic not found')
            
        this_account = Account.objects.filter(account_id=this_rhic.account_id)[0]
        contract_number = this_rhic.contract
        contracts =  Account.objects.filter(account_id=this_rhic.account_id)[0].contracts
        this_contract = find_item(lambda contract: contract.contract_id == contract_number, contracts)
        contract_products = this_contract.products
        
        this_product = ""
        for product_checkin in pu.product_info:
            for p in contract_products:
                #add additional matching logic here
                if len(p.engineering_ids) > 1:
                    _LOG.debug('found multipem product @ import')
                    product_set = Set(p.engineering_ids)
                    checkin_set = Set(pu.product_info)
                    if product_set in checkin_set:
                        this_product = p
                elif str(p.engineering_ids[0]) == str(product_checkin):
                    this_product = p
        

            rd = ReportData(instance_identifier=str(pu.instance_identifier), 
                            consumer = str(pu.consumer),
                            product = str(this_product.engineering_ids),
                            product_name = this_product.name,
                            date = pu.date,
                            hour = pu.date.strftime(hr_fmt),
                            sla = this_product.sla,
                            support = this_product.support_level,
                            contract_id = str(this_rhic.contract),
                            contract_use = str(this_product.quantity),
                            memtotal = int(pu.facts['memory_dot_memtotal']),
                            cpu_sockets = int(pu.facts['lscpu_dot_cpu_socket(s)']),
                            environment = str(pu.splice_server)
                            )
            # need to fix this so customers can 
            dupe = ReportData.objects.filter(consumer=str(pu.consumer),
                                              instance_identifier=str(pu.instance_identifier),
                                               hour=pu.date.strftime(hr_fmt),
                                                product= str(this_product.engineering_ids))
            if dupe:
                _LOG.info("found dupe:" + str(pu))
            else:
                _LOG.debug(str(this_product.engineering_ids))
                rd.save()

    end = datetime.utcnow()
    time['end'] = end.strftime(format)
    results.append(time)
    _LOG.info('import complete')
    
    return results