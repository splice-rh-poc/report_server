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

from django.contrib.auth.models import User, check_password
from passlib.hash import md5_crypt
from report_server.common import config
from mongoengine.django.auth import MongoEngineBackend

import cx_Oracle

import logging

_LOG = logging.getLogger(__name__)

DB_NAME = config.CONFIG.get('spacewalk', 'db_name')                      
DB_USER = config.CONFIG.get('spacewalk', 'db_user')               
DB_PASS = config.CONFIG.get('spacewalk', 'db_password')         
DB_HOST = config.CONFIG.get('spacewalk', 'db_host')
PORT =  config.CONFIG.get('spacewalk', 'db_port')

class SpacewalkBackend(object):
    """
    Authenticate against a spacwalk db
    """
    
    def authenticate(self, pxt_session=None):
        con_string = DB_USER + '/' + DB_PASS + '@' + DB_HOST + '/' + DB_NAME
        CON = cx_Oracle.connect(con_string)
        CURSOR = CON.cursor()        
        pxt = pxt_session.split("x")[0]
        CURSOR.execute('select WEB_USER_ID from pxtsessions where ID = '+ pxt)
        result = CURSOR.fetchone()
        web_user_id = result[0]
        if web_user_id == 'None':
            _LOG.error('spacewalk session has expired')
            return None
        
        
        CURSOR.execute('select LOGIN from web_contact WHERE ID = ' + str(web_user_id))
        result = CURSOR.fetchone()
        oracle_user_login = result[0]        
        _LOG.info('ORACLE USER: ' +  oracle_user_login)

        try:
            user = User.objects.get(username=oracle_user_login)
            _LOG.info('report server username: ' + user.username)
        except User.DoesNotExist:
            # Create a new user. Note that we can set password
            # to anything, because it won't be checked; the password
            # Another option is to decode the spacewalk user passwd
            
            user = User(username=mysession.web_user.login, password="default")
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