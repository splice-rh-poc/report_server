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

# Create your views here.
from __future__ import division
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from splice.common.utils import convert_to_datetime
from report_server.common.utils import get_dates_from_request, data_from_post, create_response
from report_server.common import constants, utils
from report_server.sreport.models import MarketingReportData
import logging
import sys

_LOG = logging.getLogger(__name__)

@login_required
def report_form(request):
    _LOG.info("space_form called by method: %s" % (request.method))
    user = str(request.user)
    environments = MarketingReportData.objects.distinct("splice_server")
    contracts = MarketingReportData.objects.distinct("contract")
    response_data = {}
    response_data['user'] = user
    response_data['environments'] = environments
    response_data['contracts'] = contracts

    _LOG.info(response_data)

    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response


@login_required
def report(request):
    
    _LOG.info("report called by method: %s" % (request.method))
    user = str(request.user)
       
    start, end = get_dates_from_request(request)
    data = data_from_post(request)
    
    if 'env' in data:
        environment = data["env"]
    else:
        environment = "All"

    contract = data["contract_number"]
    results = []
    invalid = MarketingReportData.objects.filter(status='invalid', date__gt=start, date__lt=end)
    partial = MarketingReportData.objects.filter(status='partial', date__gt=start, date__lt=end)

    if invalid:
        results.append(invalid[0])
    if partial:
        results.append(partial[0])
    format = constants.full_format

    response_data = {}
    response_data['list'] = results
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    return create_response(response_data)

def instance_detail(request):
    data = utils.data_from_post(request)
    user = str(request.user)
    #account = Account.objects.filter(login=user)[0].account_id
    instance = data["instance"]
    date = convert_to_datetime(data["date"])
    results = MarketingReportData.objects.filter(instance_identifier=instance, date=date)
    _LOG.info("in view")
    _LOG.info(results[0]["facts"])

    response_data = {}
    response_data['list'] = results

    return create_response(response_data)