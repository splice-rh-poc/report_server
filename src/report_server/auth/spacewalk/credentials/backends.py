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

from mongoengine.django.auth import User
from mongoengine.django import auth
from passlib.hash import md5_crypt
from report_server.common import config
from report_server.auth.spacewalk.db import SpacewalkDB

import logging
_LOG = logging.getLogger(__name__)



class SpacewalkBackend(object):
        
    """
    Authenticate against a spacwalk db

    Use the login name, and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'sha1$4e987$afbcf42e21bd417fb71db8c66b321e9fc33051de'
    """

    def authenticate(self, request=None, username=None, password=None):
        try:

            space_db = SpacewalkDB()
            result = space_db.execute_one("select * FROM web_contact WHERE LOGIN = '%s'" % (username))
            if config.CONFIG.get('spacewalk', 'db_backend') == 'postgresql':
                passwd_to_match = result[4]
            else:
                passwd_to_match = result[4]
            salt = passwd_to_match.split("$")[2]
            passwd_hash = md5_crypt.encrypt(password, salt=salt)
            
            if passwd_to_match == passwd_hash:
                try:
                    user = User.objects.get(username=username)
                except Exception as e:
                    _LOG.debug("User not found or exception: %s" % (str(e)))
                    # Create a new user. Note that we can set password
                    # to anything, because it won't be checked; the password
                    # from settings.py will.
                    user = User(username=username, password=password)
                    user.is_active = True
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()              
                return user
            return None
        except IndexError:
            _LOG.error('authentication failed, user does not exist in spacewalk')
            return None  
        
    

    def get_user(self, user_id):
        try:
            #the user_id = request.session[SESSION_KEY] is getting sent here
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


