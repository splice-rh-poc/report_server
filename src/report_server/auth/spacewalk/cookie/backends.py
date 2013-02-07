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

#from django.contrib.auth.models import User, check_password
from mongoengine.django.auth import User, check_password
from passlib.hash import md5_crypt
from report_server.common import config
from report_server.auth.spacewalk.db import SpacewalkDB

import logging

_LOG = logging.getLogger(__name__)

class SpacewalkBackend(object):
    """
    Authenticate against a spacwalk db
    """
    
    def authenticate(self, pxt_session=None):
  
        pxt = pxt_session.split("x")[0]
        space_db = SpacewalkDB()
        result = space_db.get_web_user(pxt)        
        web_user_id = result[0]
        if web_user_id == 'None':
            _LOG.error('spacewalk session has expired')
            return None
        
        result = space_db.get_login(web_user_id)  
        oracle_user_login = result[0]        
        _LOG.info('ORACLE USER: ' +  oracle_user_login)

        try:
            user = User.objects.get(username=oracle_user_login)
            _LOG.info('report server username: ' + user.username)
        except User.DoesNotExist:
            # Create a new user. Note that we can set password
            # to anything, because it won't be checked; the password
            # Another option is to decode the spacewalk user passwd
            
            user = User(username=oracle_user_login, password="default")
            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.save()
        return user
  

    def get_user(self, user_id):
        try:
            #the user_id = request.session[SESSION_KEY] is getting sent here
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None