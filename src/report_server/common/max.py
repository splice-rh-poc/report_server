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
from sreport.models import  ReportData, ReportDataDaily

import logging
from utils import datespan
import json
from common.utils import subscription_calc, datespan_by_hour, get_datespan
from dev.custom_count import Rules
from datetime import datetime, timedelta
from common import constants



_LOG = logging.getLogger(__name__)
rules = Rules()
report_biz_rules = rules.get_rules()

class MaxUsage:
    
    @staticmethod
    def get_product_match(start, end, contracted_use, filter_args, product_config):
        count_list = []
        f = filter_args
        delta=timedelta(days=1)
        currentDate = start
        calculation = product_config['calculation']
        contracted_use = contracted_use
        results = []
        justCount = []
        while currentDate < end:
            day = currentDate.strftime(constants.day_fmt)
            if calculation == 'hourly':
                count = ReportData.objects.filter(day=day, **filter_args).count()
            elif calculation == 'daily':
                count = ReportDataDaily.objects.filter(day=day, **filter_args).count()
            else:
                _LOG.error('check rules, unsupported format found != hourly,daily')
                raise Exception("unsupported calculation")
            results.append({'date': currentDate.strftime(constants.just_date), 'count': count})
            justCount.append(count)
            currentDate += delta
        
        return results, justCount
        
        
