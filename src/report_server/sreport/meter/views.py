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
from report_server.common import constants, utils
from report_server.common.utils import get_date_epoch, get_date_object
from report_server.common.utils import get_dates_from_request, data_from_post, create_response
from report_server.common.report import hours_per_consumer
from report_server.sreport.models import ProductUsageForm, SpliceServer
from rhic_serve.rhic_rest.models import RHIC, Account

import csv
import logging
import sys


# from report_server.sreport.models import Account, SpliceAdminGroup, SpliceUserProfile
_LOG = logging.getLogger(__name__)


@login_required
def report_form(request):
    # replaces create_report()
    _LOG.info("report_form_ui20 called by method: %s" % (request.method))

    if request.method == 'POST':
        form = ProductUsageForm(request.POST)
        if form.is_valid():
            pass
        else:
            form = ProductUsageForm()

    contracts = []
    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    list_of_contracts = Account.objects.filter(account_id=account)[0].contracts
    list_of_rhics = list(RHIC.objects.filter(account_id=account))
    environments = SpliceServer.objects.distinct("environment")
    for c in list_of_contracts:
        contracts.append(c.contract_id)

    # since some item(s) are not json-serializable,
    # extract info we need and pass it along
    # i.e. r.uuid

    response_data = {}
    response_data['contracts'] = contracts
    response_data['user'] = user
    response_data['list_of_rhics'] = [(str(r.uuid), r.name)
                                      for r in list_of_rhics]
    response_data['environments'] = environments

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
    account = Account.objects.filter(login=user)[0].account_id
       
    start, end = get_dates_from_request(request)
    data = data_from_post(request)
    
    if 'env' in data:
        environment = data["env"]
    else:
        environment = "All"

    rhic = data["rhic"]
    contract = data["contract_number"]
    list_of_rhics = []

    if contract == 'All' and (rhic == 'All' or rhic == 'null'):
        list_of_rhics = list(RHIC.objects.filter(account_id=account))

    elif rhic != 'null':
        if rhic == "All":
            list_of_rhics = list(RHIC.objects.filter(contract=contract))
        else:
            my_uuid = data['rhic']
            list_of_rhics = list(RHIC.objects.filter(uuid=my_uuid))

    else:
        list_of_rhics = list(RHIC.objects.filter(account_id=account))

    args = {'start': start,
            'end': end,
            'list_of_rhics': list_of_rhics,
            'environment': environment
            } 
    results = hours_per_consumer(**args)

    format = constants.full_format

    response_data = {}
    response_data['list'] = results
    response_data['account'] = account
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    return create_response(response_data)

def export(request):
    if request.method == 'GET':
        result = create_export_report(request)

    mydict = json.loads(result.content)
    list_of_results = mydict['list']
    start = datetime.strptime(mydict['start'], constants.full_format)
    end = datetime.strptime(mydict['end'], constants.full_format)
    filter_args_list = []
    for rhic in list_of_results:
        for products in rhic:
            filter_args_list.append(products['filter_args_dict'])
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(
        ReportData.__name__)
    writer = csv.writer(response)

    # Write data to CSV file
    for f in filter_args_list:
        thismap = json.loads(f)
        # print ReportData.objects.filter(date__gt=start, date__lt=end,
        # **thismap)
        for obj in ReportData.objects.filter(date__gt=start, date__lt=end, **thismap):
            row = [obj.consumer, obj.instance_identifier,
                   obj.product_name, obj.product, obj.hour, obj.splice_server]
            writer.writerow(row)
    # Return CSV file to browser as download
    return response


def create_export_report(request):
    _LOG.info("report called by method: %s" % (request.method))

    user = str(request.user)
    account = Account.objects.filter(login=user)[0].account_id
    start, end = get_dates_from_request(request)
    
    if 'env' in request.GET:
        environment = request.GET['env']
    else:
        environment = "All"
        
    rhic = request.GET['rhic']
    contract = request.GET['contract_number']    
    list_of_rhics = []
    
    if contract == 'All' and (rhic == 'All' or rhic == 'null'):
        list_of_rhics = list(RHIC.objects.filter(account_id=account))
        results = hours_per_consumer(start,
                                     end, 
                                     list_of_rhics=list_of_rhics,
                                     environment=environment)

    elif rhic != 'null':
        if rhic == "All":
            list_of_rhics = list(RHIC.objects.filter(contract=contract))
        else:
            my_uuid = rhic
            list_of_rhics = list(RHIC.objects.filter(uuid=my_uuid))
        results = hours_per_consumer(start,
                                     end,
                                     list_of_rhics,
                                     environment=environment)

    else:
        list_of_rhics = list(RHIC.objects.filter(account_id=account))
        results = hours_per_consumer(start,
                                     end,
                                     list_of_rhics=list_of_rhics,
                                     environment=environment)

    format = constants.full_format

    response_data = {}
    response_data['list'] = results
    response_data['account'] = account
    response_data['start'] = start.strftime(format)
    response_data['end'] = end.strftime(format)

    #return create_response(utils.to_json(response_data))
    return create_response(response_data)