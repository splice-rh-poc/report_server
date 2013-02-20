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

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.utils.importlib import import_module
import logging

_LOG = logging.getLogger(__name__)


class SpacewalkSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        engine = import_module('mongoengine.django.sessions')
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        report_session = request.COOKIES.get('report-session', None)
        """
        testing
        report_session = "33xa165e3fb2250de479f979062a03f17a6"
        """
        request.session = engine.SessionStore(session_key)
        
        if hasattr(request, 'user'):
            _LOG.info('request.user' + str(request.user))
        if report_session:
            _LOG.debug('found report session')
            request.session.__setitem__('ssession', report_session)
            try:
                user = authenticate(pxt_session=report_session)
            except IndexError:
                _LOG.error('authentication failed, cookie is not valid')
            if user:              
                request.session.__setattr__("_auth_user_id", user.id)
    
                #need to add the user attribute to be set in auth_login
                request.__setattr__("user", None)
                _LOG.info("ssession: " + report_session)
                auth_login(request, user)
            else:
                _LOG.debug('satellite session may have expired')
                request.session.flush()
                
        else:
            _LOG.debug('report session not found')
            
    
   
