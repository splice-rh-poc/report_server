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
from report_server.sreport.models import SpliceServer
from report_server.common import utils
import logging
import sys

_LOG = logging.getLogger(__name__)

@login_required
def report_form(request):
    _LOG.info("space_form called by method: %s" % (request.method))
    user = str(request.user)
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