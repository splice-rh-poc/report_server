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

#future import must be first
from __future__ import division

from datetime import datetime, timedelta
from mongoengine import OperationError, NotUniqueError
from report_server.common import config
from report_server.common import constants
from report_server.sreport.models import ReportData, ImportHistory
from report_server.sreport.models import ProductUsage, SpliceServer
from rhic_serve.rhic_rest.models import RHIC
from rhic_serve.rhic_rest.models import Account
from sets import Set
import logging

_LOG = logging.getLogger(__name__)


def import_data(product_usage=[],
                checkin_interval=1,
                from_splice_server="NA",
                force_import=False):
    """
    @param product_usage
    @type mongoengine cursor

    @param checkin_interval
    @type int
    @description the interval between client checkins range 1-23, 24=daily

    @return dict w/ keys start, end to measure how long the import took
    @rtype dict
    """
    # config fail/pass on missing rhic
    if not product_usage:
        product_usage = ProductUsage.objects.all()
    start_stop_time = []
    quarantined = []
    total_import_count = len(product_usage)
    remaining_import_count = total_import_count

    # debug
    start = datetime.utcnow()
    
    #provide a way to throttle how often import can be run
    time = {}
    time['start'] = start.strftime(constants.full_format)

    time_now = datetime.utcnow()
    threshold = 0
    if config.CONFIG.has_option('import', 'quiet_period'):
        threshold = int(config.CONFIG.get('import', 'quiet_period'))
    last_import_threshhold = time_now - timedelta(minutes=threshold)
    last_import = ImportHistory.objects.filter(
        date__gt=last_import_threshhold).count()
    
    if last_import > 0 and force_import == False:
        time['end'] = -1 # -1 send import skipped message
        start_stop_time.append(time)
        _LOG.info("import skipped")
        return [], start_stop_time
    else:
        record = ImportHistory(date=start, splice_server=from_splice_server)
        record.save()

    # committing every 100 records instead of every 1 record saves about 5
    # seconds.
    cached_rhics = {}
    cached_contracts = {}

    for pu in product_usage:
        uuid = pu.consumer
        
        #BEGIN SANITIZE THE PU DATA 
        if not pu.allowed_product_info:
            _LOG.critical('product usuage object does not have any allowed products (engineering ids)')
            continue
                
        try:
            splice_server = SpliceServer.objects.get(uuid=pu.splice_server)
            _LOG.info('splice server = ' + splice_server.hostname)
        except Exception:
            _LOG.critical('splice server named: ' + str(pu.splice_server) + ' not found')
            continue        
        
        
        if uuid in cached_rhics:
            rhic = cached_rhics[uuid]
        else:
            try:
                _LOG.info('using RHIC: ' + uuid)
                rhic = RHIC.objects.filter(uuid=uuid)[0]
                cached_rhics[uuid] = rhic
            except IndexError:
                _LOG.critical('rhic not found @ import: ' + uuid)
                _LOG.critical('product usuage object will NOT be imported')
                continue
        
        #END SANITIZE THE PU DATA 

        account = Account.objects(account_id=rhic.account_id).only('contracts').first()

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
                splice_server = SpliceServer.objects.get(uuid=pu.splice_server)

                for interval in range(checkin_interval):
                    td = timedelta(hours=interval)
                    this_time = pu.date + td
                    rd = ReportData(
                        instance_identifier=str(pu.instance_identifier),
                        consumer=rhic.name,
                        consumer_uuid=uuid,
                        product=product.engineering_ids,
                        product_name=product.name,
                        date=this_time,
                        hour=this_time.strftime(
                            constants.hr_fmt),
                        day=pu.date.strftime(
                            constants.day_fmt),
                        sla=product.sla,
                        support=product.support_level,
                        contract_id=rhic.contract,
                        contract_use=str(product.quantity),
                        memtotal=int(
                            pu.facts['memory_dot_memtotal']),
                        cpu_sockets=int(
                            pu.facts['lscpu_dot_cpu_socket(s)']),
                        cpu=int(
                            pu.facts['lscpu_dot_cpu(s)']),
                        environment=str(
                            splice_server.environment),
                        splice_server=str(
                            splice_server.hostname),
                        duplicate=interval,
                        record_identifier=rhic.name + 
                            str(pu.instance_identifier) +
                            pu.date.strftime(constants.day_fmt) +
                            product.name
                    )

                    try:
                        rd.save(safe=True)
                        _LOG.info(
                            'recording: ' + str(product.engineering_ids))
                    except NotUniqueError:
                        _LOG.info("Ignorning NotUniqueError for: %s" % (rd))
                    except OperationError as oe:
                        _LOG.info("could not import:" +
                                  str(pu) + "Exception: " + str(oe))
                        quarantined.append(rd)

    end = datetime.utcnow()
    time['end'] = end.strftime(constants.full_format)
    start_stop_time.append(time)
    _LOG.info('import complete')

    return quarantined, start_stop_time
