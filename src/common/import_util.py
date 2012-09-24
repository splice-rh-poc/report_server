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
from sreport.models import ReportData
#from splice.entitlement.models import ProductUsage
from splice.entitlement.models import SpliceServer
from sreport.models import ProductUsage
#from rhic_serve.rhic_rcs.models import RHIC
from rhic_serve.rhic_rest.models import RHIC
from rhic_serve.rhic_rest.models import Account

from datetime import datetime
from common.utils import find_item
from sets import Set

_LOG = logging.getLogger("sreport.import_util")

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
    
    seen_rhics = {}
    
    for rhic in RHIC.objects.all():
        _LOG.info(rhic.uuid)
    for pu in pu_all:
        my_uuid = str(pu.consumer)

        if my_uuid in seen_rhics:
            this_rhic = seen_rhics[my_uuid]
        else:
            try:
                _LOG.info('using RHIC: ' + my_uuid)
                this_rhic = RHIC.objects.filter(uuid=my_uuid)[0]
                # seen_rhics[my_uuid] = this_rhic
            except IndexError:
                _LOG.critical('rhic not found @ import')
                raise Exception('rhic not found')
            
        this_account = Account.objects.filter(account_id=this_rhic.account_id)[0]
        contract_number = this_rhic.contract
        contracts =  Account.objects.filter(account_id=this_rhic.account_id)[0].contracts
        this_contract = find_item(lambda contract: contract.contract_id == contract_number, contracts)
        contract_products = this_contract.products
        
        for product_checkin in pu.allowed_product_info:
            for p in contract_products:
                product_candidate = None
                product_match = None
                #add additional matching logic here
                if len(p.engineering_ids) > 1:
                    _LOG.debug('found multipem product @ import')
                    product_set = Set(p.engineering_ids)
                    checkin_set = Set(pu.allowed_product_info)
                    if product_set == checkin_set:
                        product_candidate = p
                elif str(p.engineering_ids[0]) == str(product_checkin):
                    product_candidate = p
                    _LOG.debug('product:' + str(p))
                else:
                    continue

                if (product_candidate.sla == this_rhic.sla and
                   product_candidate.support_level == this_rhic.support_level):
                    product_match = product_candidate

                if product_match:
                    rd = ReportData(
                                    instance_identifier = str(pu.instance_identifier),
                                    consumer = this_rhic.name, 
                                    consumer_uuid = str(pu.consumer),
                                    product = str(product_match.engineering_ids),
                                    product_name = product_match.name,
                                    date = pu.date,
                                    hour = pu.date.strftime(hr_fmt),
                                    sla = product_match.sla,
                                    support = product_match.support_level,
                                    contract_id = str(this_rhic.contract),
                                    contract_use = str(product_match.quantity),
                                    memtotal = int(pu.facts['memory_dot_memtotal']),
                                    cpu_sockets = int(pu.facts['lscpu_dot_cpu_socket(s)']),
                                    #environment = str(pu.splice_server.environment),
                                    splice_server = str(pu.splice_server)
                                    )
                    # need to fix this so customers can 
                    dupe = ReportData.objects.filter(consumer=str(pu.consumer),
                                                      instance_identifier=str(pu.instance_identifier),
                                                       hour=pu.date.strftime(hr_fmt),
                                                        product= str(product_match.engineering_ids))
                    if dupe:
                        _LOG.info("found dupe:" + str(pu))
                    else:
                        _LOG.info('recording: ' + str(product_match.engineering_ids))
                        rd.save()

    end = datetime.utcnow()
    time['end'] = end.strftime(format)
    results.append(time)
    _LOG.info('import complete')
    
    return results
