# Copyright 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from report_server.sreport.models import ProductUsage, QuarantinedReportData,\
    ReportData
from report_server.sreport import views
from report_server.common import utils
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.resources import Resource
from django.http import HttpResponse
import logging, sys


from report_server.common import import_util
from report_server.report_import.api import productusage

_LOG = logging.getLogger("sreport.api")

class ProductUsageResource(productusage.ProductUsageResource):

    def import_hook(self, product_usage):
        _LOG.debug("in import_hook")
        items_not_imported, start_stop_time =  import_util.import_data(product_usage, force_import=True)
        _LOG.debug("items_not_imported length: " + str(len(items_not_imported)))
        for i in items_not_imported:
            thisDict = i.to_dict()
            thisItem = QuarantinedReportData(**thisDict)
            thisItem.save()
            
        return items_not_imported
    
    


class QuarantinedDataResource(Resource):

    class Meta:
        queryset = QuarantinedReportData.objects.all()
        authorization = Authorization()
        allowed_methods = ['get']

    
    
    def get_list(self, request, **kwargs):
        _LOG.info("QuarantinedDataResource::get_list() ")
        
        results = QuarantinedReportData.objects.all()
        response_data = {}
        response_data['list'] = results

        try:
            response = HttpResponse(utils.to_json(response_data))
        except:
            _LOG.error(sys.exc_info()[0])
            _LOG.error(sys.exc_info()[1])
            raise
    
        return response

class ComplianceDataResource(Resource):
    
    class Meta:
        queryset = ReportData.objects.all()
        authorization = Authorization()
        allowed_methods = ['get']
        
    def get_list(self, request, **kwargs):
        
        _LOG.info("ComplianceDataResource::get_list() ")
        
        response = views.systemFactCompliance(request)

        return response


