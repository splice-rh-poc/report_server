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
from report_server.sreport.models import  ReportData, ReportDataDaily

import logging
from report_server.common.custom_count import Rules
from datetime import datetime, timedelta
from report_server.common import constants
from rhic_serve.rhic_rest.models import RHIC
from rhic_serve.rhic_rest.models import Account




_LOG = logging.getLogger(__name__)
rules = Rules()
report_biz_rules = rules.get_rules()

class MaxUsage:
    
    
    @staticmethod
    def get_MDU_MCU(start, end, filter_args, product_name):
        count_list = []
        f = filter_args
        delta=timedelta(days=1)
        currentDate = start
        calculation = 'hourly'
        results = []
        mdu_count = []
        mcu_count = []
        date = []
        daily_highest_concurrent_usage = 0
        contract_quantity = get_product_info(f, product_name)
        daily_contract = []
        
        
        
        while currentDate < end:
            hourly_highest_concurrent_usage = 0
            day = currentDate.strftime(constants.day_fmt)
            if calculation == 'hourly':
                mdu_each = ReportData.objects.filter(day=day, **filter_args).distinct("instance_identifier")
                mdu = len(mdu_each)
                
            elif calculation == 'daily':
                mdu = ReportDataDaily.objects.filter(day=day, **filter_args).count()
            else:
                _LOG.error('check rules, unsupported format found != hourly,daily')
                raise Exception("unsupported calculation")

            hour_delta = timedelta(hours=1)
            currentHour = datetime.strptime(currentDate.strftime(constants.day_fmt), constants.day_fmt)
            for h in range(24):
                this_hour = currentHour.strftime(constants.hr_fmt)
                mcu = ReportData.objects.filter(hour=this_hour, **filter_args).count()
                if mcu > hourly_highest_concurrent_usage:
                    hourly_highest_concurrent_usage = mcu
                
                currentHour += hour_delta
                
            #The highest number is the count
            mcu = hourly_highest_concurrent_usage
            
            results.append({'date': currentDate.strftime(constants.just_date), 'mdu': mdu, 'mcu': mcu})
            mdu_count.append([currentDate.strftime(constants.jqplot_fmt), mdu])
            mcu_count.append([currentDate.strftime(constants.jqplot_fmt), mcu])
            daily_contract.append([currentDate.strftime(constants.jqplot_fmt), contract_quantity])
            date.append(currentDate.strftime(constants.jqplot_fmt))
            
            currentDate += delta
        
        return results, mdu_count, mcu_count, daily_contract, date
    

    @staticmethod
    def get_MCU_Compliant(start, end, filter_args, product_name):
        compliant = True
        count_list = []
        f = filter_args
        delta=timedelta(days=1)
        currentDate = start
        calculation = 'hourly'
        results = []
        mdu_count = []
        mcu_count = []
        date = []
        daily_highest_concurrent_usage = 0
        daily_contract = []
        contract_quantity = get_product_info(f, product_name)
        
        
        
        while currentDate < end:
            hourly_highest_concurrent_usage = 0
            day = currentDate.strftime(constants.day_fmt)
            if calculation == 'hourly':
                mdu_each = ReportData.objects.filter(day=day, **filter_args).distinct("instance_identifier")
                mdu = len(mdu_each)
                
            elif calculation == 'daily':
                mdu = ReportDataDaily.objects.filter(day=day, **filter_args).count()
            else:
                _LOG.error('check rules, unsupported format found != hourly,daily')
                raise Exception("unsupported calculation")
            
            if mdu > contract_quantity:

                hour_delta = timedelta(hours=1)
                currentHour = datetime.strptime(currentDate.strftime(constants.day_fmt), constants.day_fmt)
                for h in range(24):
                    this_hour = currentHour.strftime(constants.hr_fmt)
                    mcu = ReportData.objects.filter(hour=this_hour, **filter_args).count()
                    if mcu > hourly_highest_concurrent_usage:
                        hourly_highest_concurrent_usage = mcu
                    
                    currentHour += hour_delta
                    
                #The highest number is the count
                mcu = hourly_highest_concurrent_usage
                
                if mcu > contract_quantity:
                    return False

            
            currentDate += delta
        
        return compliant
    


def get_product_info(filter_args, product_name):
    contract_num = filter_args['contract_id']
    rhic_uuid = filter_args['consumer_uuid']
    eng_product = filter_args['product']
    sla = filter_args['sla']
    support = filter_args['support']
    
    account_num = RHIC.objects.get(uuid=rhic_uuid).account_id
    contract_list = Account.objects.filter(account_id=account_num)[0].contracts
    quantity = 0;
    count = 0
    for contract in contract_list:
        if contract.contract_id == contract_num:
            list_of_products = contract.products
            for product in list_of_products:
                if product.engineering_ids == eng_product and product.sla == sla and \
                    product.support_level == support and product.name == product_name:
                    count += 1
                    quantity = product.quantity
                    if count > 1:
                        _LOG.error("too many matches for a product, sla, support_level combination");
                        raise Exception("too many matches for a product, sla, support_level combination")
    return quantity
