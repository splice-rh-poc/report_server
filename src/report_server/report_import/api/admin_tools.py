# -*- coding: utf-8 -*-
#
# Copyright © 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import logging
import time

from django.template.response import TemplateResponse

from tastypie.authorization import Authorization
from tastypie import http
from tastypie_mongoengine.resources import MongoEngineResource
from report_server.sreport.models import  QuarantinedReportData
from report_server.common.utils import MongoEncoder
from django.http import HttpResponse
import json
from bson import json_util


_LOG = logging.getLogger(__name__)



class QuarantinedDataResource(MongoEngineResource):

    class Meta:
        queryset = QuarantinedReportData.objects.all()
        authorization = Authorization()

    
    
    def get_list(self, request, **kwargs):
        _LOG.info("QuarantinedDataResource::get_list() ")
        
        results = QuarantinedReportData.objects.all()
        response_data = {}
        response_data['list'] = results

        try:
            response = HttpResponse(MongoEncoder.to_json(response_data))
        except:
            _LOG.error(sys.exc_info()[0])
            _LOG.error(sys.exc_info()[1])
            raise
    
        return response


