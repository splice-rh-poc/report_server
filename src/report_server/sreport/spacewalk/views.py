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
from django.template.defaultfilters import slugify
from report_server.common.utils import get_dates_from_request, data_from_post, create_response
from report_server.common import constants, utils
from report_server.sreport.models import MarketingReportData, Pool
from splice.common.utils import convert_to_datetime
from splice.common import config

import csv
import json
import logging
import sys

_LOG = logging.getLogger(__name__)

@login_required
def report_form(request):
    _LOG.info("space_form called by method: %s" % (request.method))
    user = str(request.user)
    environments = MarketingReportData.objects.distinct("splice_server")
    status = MarketingReportData.objects.distinct("status")
    sys_id = MarketingReportData.objects.distinct("systemid")
    response_data = {}
    response_data['user'] = user
    response_data['environments'] = environments
    response_data['status'] = status
    response_data['sys_host'] = ['mock_host1', 'mock_host2']
    response_data['sys_id'] = sys_id

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

    status = data["status"]
    results = []
    _LOG.info("status =" + status)
    if status == "All":
        results  = MarketingReportData.objects.filter(date__gt=start, date__lt=end)
        #r  = MarketingReportData.objects.all()
    elif status == "valid":
        results = MarketingReportData.objects.filter(status='valid', date__gt=start, date__lt=end)
    elif status == "invalid":
        results = MarketingReportData.objects.filter(status='invalid', date__gt=start, date__lt=end)
    elif status == "partial":
        results = MarketingReportData.objects.filter(status='partial', date__gt=start, date__lt=end)
    elif status == "Failed":
        invalid = MarketingReportData.objects.filter(status='invalid', date__gt=start, date__lt=end)
        partial = MarketingReportData.objects.filter(status='partial', date__gt=start, date__lt=end)
        if invalid:
            results.append(invalid[0])
        if partial:
            results.append(partial[0])

    if results:
        _LOG.info(len(results))

    num_valid = MarketingReportData.objects.filter(status='valid', date__gt=start, date__lt=end).count()
    num_invalid = MarketingReportData.objects.filter(status='invalid', date__gt=start, date__lt=end).count()
    num_partial = MarketingReportData.objects.filter(status='partial', date__gt=start, date__lt=end).count()
    
    format = constants.full_format

    response_data = {}
    response_data['list'] = results
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)
    response_data['num_valid'] = str(num_valid)
    response_data['num_invalid'] = str(num_invalid)
    response_data['num_partial'] = str(num_partial)

    return create_response(response_data)

def instance_detail(request):
    data = utils.data_from_post(request)
    user = str(request.user)
    #account = Account.objects.filter(login=user)[0].account_id
    instance = data["instance"]
    date = convert_to_datetime(data["date"])
    results = MarketingReportData.objects.filter(instance_identifier=instance, date=date)[0]


    response_data = {}
    response_data['space_hostname'] = config.CONFIG.get('spacewalk', 'db_host')
    response_data['facts'] = results["facts"]
    response_data['product_info'] = results["product_info"]
    response_data['status'] = results["status"]
    response_data['splice_server'] = results["splice_server"]
    response_data['system_id'] = results["systemid"]
    response_data['instance_identifier'] = results["instance_identifier"]
    response_data['date'] = results["date"]

    return create_response(response_data)

def subscription_detail(request):
    data = utils.data_from_post(request)
    product_id = data["product_id"]
    result = Pool.objects.filter(product_id=product_id)[0]
    provided_products = json.dumps(result['provided_products'])
    product_attributes = json.dumps(result['product_attributes'])
    response_data = {}
    response_data['pool_detail'] = result
    response_data['provided_products'] = provided_products
    response_data['product_attributes'] = product_attributes
    

    return create_response(response_data)

def export(request):
    #if request.method == 'GET':
    start, end = get_dates_from_request(request)
    status = request.GET["status"]
    environment = request.GET['env']

    _LOG.info(status)
    _LOG.info(environment)

    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(
        MarketingReportData.__name__)
    writer = csv.writer(response)

    if status == "All":
        for obj in MarketingReportData.objects.filter(date__gt=start, date__lt=end):
            _LOG.info(obj.product_info)
            products = json.loads(obj.product_info)
            _LOG.info(products)
            for p in products:
                row = [obj.instance_identifier, obj.hour, obj.splice_server, p["product_id"], 
                p["product_account"], p["product_contract"], p["product_quantity"], p["pool_uuid"]]
                writer.writerow(row)
            # Return CSV file to browser as download
    else:
        for obj in MarketingReportData.objects.filter(status=status, date__gt=start, date__lt=end):
            row = [obj.instance_identifier, obj.hour, obj.splice_server]
            writer.writerow(row)

    return response

