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


import json
from bson import json_util

from splice.common.models import ProductUsage

_LOG = logging.getLogger(__name__)

class ProductUsageResource(MongoEngineResource):

    class Meta:
        queryset = ProductUsage.objects.all()
        authorization = Authorization()


    def post_list(self, request, **kwargs):
        _LOG.info("ProductUsageResource::post_list() processing %s KB." % (len(request.raw_post_data)/1024.0))

        #deserialized = self.deserialize(
        #    request, request.raw_post_data,
        #    format=request.META.get('CONTENT_TYPE', 'application/json'))
        #deserialized = self.alter_deserialized_detail_data(
        #    request, deserialized)
        #bundle = self.build_bundle(data=deserialized, request=request)
        #_LOG.info("bundle = %s" % (bundle))
        a = time.time()
        product_usage = json.loads(request.raw_post_data, object_hook=json_util.object_hook)
        if isinstance(product_usage, dict):
            product_usage = [product_usage]
        pu_models = [ProductUsage._from_son(p) for p in product_usage]
        b = time.time()
        items_not_imported = self.import_hook(pu_models)
        c = time.time()
        _LOG.info("ProductUsageResource::post_list() Total Time: %s,  %s seconds to convert %s KB to JSON. "
                  "%s seconds to import %s objects into mongo." % (c-a, b-a, len(request.raw_post_data)/1024.0, c-b, len(pu_models)))
        if not items_not_imported:
            return http.HttpAccepted()
        else:
            return http.HttpConflict()

    def get_list(self, request, **kwargs):
        product_usage = ProductUsage.objects.all()
        results = self.import_hook(product_usage)
        response = TemplateResponse(request, 'import.html', {'list': results})
        return response

# import hook is overriden in sreport.api
    def import_hook(self, product_usage):
        """
        @param product_usage:
        @return: a list of items which failed to import.
        """
        raise NotImplementedError

