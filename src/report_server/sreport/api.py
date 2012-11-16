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

from report_server.sreport.models import ProductUsage, QuarantinedReportData
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
import logging

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
    
    
