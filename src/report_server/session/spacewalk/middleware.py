

from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.utils.importlib import import_module
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend

import logging
import time

_LOG = logging.getLogger(__name__)

class SpacewalkSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        report_session = request.COOKIES.get('report-session', None)
        """
        testing
        report_session = "33xa165e3fb2250de479f979062a03f17a6"
        """
        #report_session = "139x79c46a01c21ef935a542fb365412339a"
        request.session = engine.SessionStore(session_key)
        
        if hasattr(request, 'user'):
            _LOG.info('request.user' + str(request.user))
        if report_session:
            _LOG.debug('found report session')
            request.session.__setitem__('ssession', report_session)
            user = authenticate(pxt_session=report_session)
            if user:
                backend_id = request.session.get(BACKEND_SESSION_KEY)
                
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
            #request.session.flush()
            

    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        """
        try:
            accessed = request.session.accessed
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = cookie_date(expires_time)
                # Save the session data and refresh the client cookie.
                request.session.save()
                response.set_cookie(settings.SESSION_COOKIE_NAME,
                        request.session.session_key, max_age=max_age,
                        expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None)
        return response
