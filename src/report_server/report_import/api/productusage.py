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

from bson import json_util
from django.template.response import TemplateResponse
from tastypie.authorization import Authorization
from tastypie import http
from tastypie_mongoengine.resources import MongoEngineResource
from splice.common.models import ProductUsage

import logging
import json
import time

_LOG = logging.getLogger(__name__)

class ProductUsageResource(MongoEngineResource):

    class Meta:
        queryset = ProductUsage.objects.all()
        authorization = Authorization()


    def post_list(self, request, **kwargs):
        if not request.raw_post_data:
            _LOG.info("Empty body in request")
            return http.HttpBadRequest("Empty body in request")
        try:
            _LOG.info("ProductUsageResource::post_list() processing %s KB." % (len(request.raw_post_data)/1024.0))
            a = time.time()
            product_usage = json.loads(request.raw_post_data, object_hook=json_util.object_hook)
            if isinstance(product_usage, dict):
                product_usage = [product_usage]
            pu_models = [ProductUsage._from_son(p) for p in product_usage]
            b = time.time()
            items_not_imported = self.import_hook(pu_models)
            c = time.time()
            _LOG.info("ProductUsageResource::post_list() Total Time: %s,  %s seconds to convert %s KB to JSON. "
                  "%s seconds to import %s objects into mongo with %s errors." % (c-a, b-a,
                        len(request.raw_post_data)/1024.0, c-b, len(pu_models), items_not_imported))
            if not items_not_imported:
                return http.HttpAccepted("%s entries imported" % (len(pu_models)))
            else:
                return http.HttpConflict("%s entries imported, %s entries not imported or error" % \
                                         (len(pu_models - len(items_not_imported)), items_not_imported))
        except Exception, e:
            _LOG.exception("Unable to process request with %s bytes in body" % (len(request.raw_post_data)))
            return http.HttpBadRequest(e)

# import hook is overriden in sreport.api
    def import_hook(self, product_usage):
        """
        @param product_usage:
        @return: a list of items which failed to import.
        """
        raise NotImplementedError

