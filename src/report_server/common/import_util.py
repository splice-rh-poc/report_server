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
from sreport.models import ProductUsage, SpliceServer
from rhic_serve.rhic_rest.models import RHIC
from rhic_serve.rhic_rest.models import Account
from datetime import datetime, timedelta

from datetime import datetime
from sets import Set
from common import config

_LOG = logging.getLogger("sreport.import_util")

def import_data(product_usage=ProductUsage.objects.all(), use_bulk_load=False, checkin_interval=1):
    #config fail/pass on missing rhic
    config.init()
    this_config = config.get_import_info()
    total_import_count = len(product_usage)
    remaining_import_count = total_import_count

    results = []
    #debug
    full_format = "%a %b %d %H:%M:%S %Y"
    start = datetime.utcnow()
    time = {}
    time['start'] = start.strftime(full_format)
    #debug
    
    hr_fmt = "%m%d%Y:%H"
    
    # committing every 100 records instead of every 1 record saves about 5
    # seconds.
    commit_count = 500
    cached_rhics = {}
    cached_contracts = {}
    rds = {}
    
    for pu in product_usage:
        uuid = pu.consumer

        if uuid in cached_rhics:
            rhic = cached_rhics[uuid]
        else:
            try:
                _LOG.info('using RHIC: ' + uuid)
                rhic = RHIC.objects.filter(uuid=uuid)[0]
                cached_rhics[uuid] = rhic
            except IndexError:
                _LOG.critical('rhic not found @ import: ' + uuid)
                if this_config['continue_on_error'] == '0':
                    raise Exception('rhic not found: ' + uuid)
                else:
                    continue
            
        account = Account.objects(
            account_id=rhic.account_id).only('contracts').first()

        contract = None
        if rhic.contract in cached_contracts:
            contract = cached_contracts['rhic.contract']
        else:
            for c in account.contracts:
                if c.contract_id == rhic.contract:
                    cached_contracts['rhic.contract'] = c
                    contract = c
                    break

        # Set of used engineering ids for this checkin
        product_set = Set(pu.allowed_product_info)

        # Iterate over each product in the contract, see if it matches sla and
        # support level, and consumed engineering ids.  If so, save an instance
        # of ReportData
        for product in contract.products:
            # Match on sla and support level
            if not (product.sla == rhic.sla and 
               product.support_level == rhic.support_level):
                continue

            # Set of engineering ids for this product.
            product_eng_id_set = set(product.engineering_ids)

            # If the set of engineering ids for the product is a subset of the
            # used engineering ids for this checkin, create an instance of
            # ReportData, check for dupes, and save the instance.
            if product_eng_id_set.issubset(product_set):
                # This line isn't technically necessary, but it improves
                # performance by making the set we need to search smaller each
                # time.
                product_set.difference_update(product_eng_id_set) 
                try:
                    splice_server = SpliceServer.objects.get(id=pu.splice_server.id)
                except AttributeError:
                    splice_server = SpliceServer.objects.get(
                        id=pu.splice_server['$id']['$oid'])
                
                  
                for interval in range(checkin_interval):
                    td = timedelta(hours=interval)
                    this_time = pu.date + td
                    rd = ReportData(instance_identifier = str(pu.instance_identifier),
                                    consumer = rhic.name, 
                                    consumer_uuid = uuid,
                                    product = product.engineering_ids,
                                    product_name = product.name,
                                    date = this_time,
                                    hour = this_time.strftime(hr_fmt),
                                    sla = product.sla,
                                    support = product.support_level,
                                    contract_id = rhic.contract,
                                    contract_use = str(product.quantity),
                                    memtotal = int(pu.facts['memory_dot_memtotal']),
                                    cpu_sockets = int(pu.facts['lscpu_dot_cpu_socket(s)']),
                                    cpu = int(pu.facts['lscpu_dot_cpu(s)']),
                                    environment = str(splice_server.environment),
                                    splice_server = str(splice_server.hostname),
                                    duplicate = interval
                                    )
    
                    # If there's a dupe, log it instead of saving a new record.
                    dupe = ReportData.objects.filter(
                        consumer_uuid=str(rhic.uuid), 
                        instance_identifier=str(pu.instance_identifier),
                        hour=this_time.strftime(hr_fmt),
                        product= product.engineering_ids)
                    if dupe:
                        _LOG.info("found dupe:" + str(pu))
                        if interval == 0:
                            _LOG.info("The duplicate is superseded by a real checkin :" + str(pu))
                            dupe.delete()
                            rd.save()
                    else:
                        if not use_bulk_load:
                            _LOG.info('recording: ' + str(product.engineering_ids))
                            rd.save()
                        else:
                            dupe_check = ("%s%s%s%s" % (str(rd.consumer_uuid), rd.instance_identifier, str(rd.hour),  str(rd.product))).__hash__()
                            #print(dupe_check)
                            rds[dupe_check]=rd
    
                            #Insert into db if requirements met
                            if remaining_import_count < commit_count:
                                num = len(rds)
                                ReportData.objects.insert(rds.values())
                                rds = {}
                                remaining_import_count -= num
                             
                            elif len(rds) >= commit_count:
                                ReportData.objects.insert(rds.values())
                                rds = {}
                                remaining_import_count -= commit_count
                                #print(remaining_import_count)
                        
                            
                        
                            

    
    end = datetime.utcnow()
    time['end'] = end.strftime(full_format)
    results.append(time)
    _LOG.info('import complete')
    
    return results
