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
from datetime import datetime, timedelta
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.models import User
from mongoengine.django.auth import User
from django.db.models.base import get_absolute_url
from django.db.models.loading import get_model
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import ensure_csrf_cookie

from report_server.common import constants, utils
from report_server.common.biz_rules import Rules
from report_server.common.import_util import import_data
from report_server.common.max import MaxUsage
from report_server.common.report import hours_per_consumer
from report_server.common.utils import get_date_epoch, get_date_object
from report_server.sreport.models import ProductUsageForm, ReportData
from report_server.sreport.models import SpliceServer, QuarantinedReportData
#from report_server.sreport.models import Account, SpliceAdminGroup, SpliceUserProfile
from rhic_serve.rhic_rest.models import RHIC, Account, SpliceAdminGroup


import logging
import json
import sys

_LOG = logging.getLogger(__name__)

@login_required
def report_form(request):
    _LOG.info("space_form called by method: %s" % (request.method))

    """
    if request.method == 'POST':
        form = ProductUsageForm(request.POST)
        if form.is_valid():
            pass
        else:
            form = ProductUsageForm()
    """

    contracts = []
    user = str(request.user)
    account = User.objects.filter(username=user)[0].id
    list_of_contracts = []
    list_of_rhics = []
    environments = SpliceServer.objects.distinct("environment")

    response_data = {}
    response_data['user'] = user
    response_data['environments'] = environments

    _LOG.info(response_data)

    try:
        response = HttpResponse(utils.to_json(response_data))
    except:
        _LOG.error(sys.exc_info()[0])
        _LOG.error(sys.exc_info()[1])
        raise

    return response