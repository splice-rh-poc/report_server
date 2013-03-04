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
from report_server.sreport.models import ReportData
from report_server.common import constants
from report_server.common import utils
from rhic_serve.rhic_rest.models import RHIC
from rhic_serve.rhic_rest.models import Account
import logging

_LOG = logging.getLogger(__name__)


class MaxUsage:

    @staticmethod
    def get_MDU_MCU(**kwargs):
        start = utils.get_date_object(kwargs["start"])
        end = utils.get_date_object(kwargs["end"])
        filter_args = kwargs["filter_args_dict"]
        product_name = kwargs["description"]["Product"]
        results = []
        mdu_count = []
        mcu_count = []
        date = []
        daily_contract = []

        currentDate = start
        f = filter_args
        delta = timedelta(days=1)
        calculation = 'hourly'
        contract_quantity = get_product_info(f, product_name)

        while currentDate < end:
            hourly_highest_concurrent_usage = 0
            day = currentDate.strftime(constants.day_fmt)
            if calculation == 'hourly':
                #Find the number of instances that checked in that day
                mdu_each = ReportData.objects.filter(day=day, **filter_args)
                mdu = len(mdu_each.distinct("instance_identifier"))

            else:
                _LOG.error('check rules, unsupported format found != hourly')
                raise Exception("unsupported calculation")

            hour_delta = timedelta(hours=1)
            currentHour = datetime.strptime(day, constants.day_fmt)
            
            #Find the highest concurrent usuage in a 24 hour period
            for h in range(24):
                this_hour = currentHour.strftime(constants.hr_fmt)
                mcu = ReportData.objects.filter(hour=this_hour, **filter_args).count()
                if mcu > hourly_highest_concurrent_usage:
                    hourly_highest_concurrent_usage = mcu

                currentHour += hour_delta

            # The highest number is the count
            mcu = hourly_highest_concurrent_usage

            results.append({'date': currentDate.strftime(constants.just_date),
                            'mdu': mdu,
                            'mcu': mcu}
                           )
            
            this_date = currentDate.strftime(constants.jqplot_fmt)
            mdu_count.append([this_date, mdu])
            mcu_count.append([this_date, mcu])
            daily_contract.append([this_date, contract_quantity])
            date.append(this_date)

            currentDate += delta

        payload = {"list": results,
                   "mdu": mdu_count,
                   "mcu": mcu_count,
                   "daily_contract": daily_contract,
                   "date": date
                   }
        return payload

    @staticmethod
    def get_MCU_Compliant(start, end, filter_args, product_name):
        compliant = True
        f = filter_args
        delta = timedelta(days=1)
        currentDate = start
        calculation = 'hourly'
        contract_quantity = get_product_info(f, product_name)

        while currentDate < end:
            hourly_highest_concurrent_usage = 0
            day = currentDate.strftime(constants.day_fmt)
            if calculation == 'hourly':
                mdu_each = ReportData.objects.filter(day=day, **filter_args)
                mdu = len(mdu_each.distinct("instance_identifier"))
            else:
                _LOG.error('check rules, unsupported format found != hourly,daily')
                raise Exception("unsupported calculation")

            if mdu > contract_quantity:
                hour_delta = timedelta(hours=1)
                currentHour = datetime.strptime(day, constants.day_fmt)
                for h in range(24):
                    this_hour = currentHour.strftime(constants.hr_fmt)
                    mcu = ReportData.objects.filter(hour=this_hour, **filter_args).count()
                    if mcu > hourly_highest_concurrent_usage:
                        hourly_highest_concurrent_usage = mcu

                    currentHour += hour_delta

                # The highest number is the count
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
    quantity = 0
    count = 0
    for contract in contract_list:
        if contract.contract_id == contract_num:
            list_of_products = contract.products
            for product in list_of_products:
                conditions = [product.engineering_ids == eng_product,
                              product.sla == sla,
                              product.support_level == support,
                              product.name == product_name
                              ]

                if all(conditions):
                    count += 1
                    quantity = product.quantity
                    if count > 1:
                        _LOG.error("too many matches for a product, sla,"
                                   "support_level combination")
                        raise Exception("too many matches for a product,"
                                        "sla, support_level combination")
    return quantity
