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


from django.http import HttpResponse
from django.contrib.auth.models import User
from report_server.sreport.models import QuarantinedReportData
from report_server.sreport.models import ReportData
from report_server.sreport import views
from report_server.common import utils
from report_server.common import import_util
from report_server.report_import.api import productusage
from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication, MultiAuthentication
from tastypie.authentication import SessionAuthentication
from tastypie_mongoengine.resources import MongoEngineResource
from tastypie.serializers import Serializer
from tastypie.resources import Resource
import logging
import json
import sys
import types


_LOG = logging.getLogger("sreport.api")


class RestSerializer(Serializer):
    """
    Class for overriding various aspects of the default Tastypie Serializer
    class.
    """

    def format_datetime(self, data):
        """
        By default, Tastypie's serializer serializes all datetime objects as
        naive (no timezone info).  I'm not sure why this is the case.

        There's a patch, but it has not been merged into master Tastypie:
        https://github.com/toastdriven/django-tastypie/commit/542d365d7d975a90c64c4c375257e5bc4b3b220a
        """
        return data.isoformat()


class ProductUsageResource(productusage.ProductUsageResource):

    def import_hook(self, product_usage):
        _LOG.debug("in import_hook")
        items_not_imported, start_stop_time = import_util.import_data(
            product_usage,
            force_import=True
        )
        _LOG.debug(
            "items_not_imported length: " + str(len(items_not_imported)))
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


class ReportResource(MongoEngineResource):

    class Meta:
        queryset = ReportData.objects.all()
        allow_methods = ['post']

        # Make sure we always get back the representation of the resource back
        # on a POST.
        # always_return_data = True

        # All Resources require basic authentication (for now).
        authentication = BasicAuthentication()
        authorization = Authorization()

    def post_list(self, request, **kwargs):
        # data = json.loads(request.raw_post_data,
        # object_hook=json_util.object_hook)
        #data = json.loads(request.raw_post_data)
        _LOG.info("ReportResource::post_list() ")
        
        """
        Horrible hack for now just to validate that the test and api are 
        working as designed.  I think one way to move forward in the proper way
        is to use a tastypie api key to get the appropriate user.
        
        As it stands any authorized, but unauthenticated request will use the
        shadowman@redhat.com User
        """

        user = request.user

        response = views.report_ui20(request)

        return response
