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


from report_server import settings


import logging
from report_server.common import config
import time

_LOG = logging.getLogger(__name__)
global DBCON 

if config.CONFIG.has_option('spacewalk', 'db_backend'):
    DB_BACKEND = config.CONFIG.get('spacewalk', 'db_backend')
    DB_NAME = config.CONFIG.get('spacewalk', 'db_name')                      
    DB_USER = config.CONFIG.get('spacewalk', 'db_user')               
    DB_PASS = config.CONFIG.get('spacewalk', 'db_password')         
    DB_HOST = config.CONFIG.get('spacewalk', 'db_host')
    PORT =  config.CONFIG.get('spacewalk', 'db_port')    
    
    if DB_BACKEND == 'postgresql':
        import psycopg2
        DBCON = psycopg2.connect(database=DB_NAME,
                                  user=DB_USER,
                                  password=DB_PASS,
                                  host=DB_HOST,
                                  port=PORT)
        
    else:
        import cx_Oracle
        con_string = DB_USER + '/' + DB_PASS + '@' + DB_HOST + '/' + DB_NAME
        DBCON = cx_Oracle.connect(con_string) 
    _LOG.info('connected to spacewalk %s database named %s' % (DB_BACKEND,DB_NAME))

class SpacewalkDB():
    
    def __init__(self):
        global DBCON
        self.DBCON = DBCON 
        self.login = None
        self.web_user = None
               
    
    def get_login(self, web_user_id=None):
        time.sleep(1)
        cursor = self.DBCON.cursor() 
        cursor.execute('select LOGIN from web_contact WHERE ID = ' + str(web_user_id))
        result = cursor.fetchone()
        print('get_login: ' + str(result))
        self.login = result
        cursor.close()
        return self.login
    
    def get_web_user(self, pxt=None):
        time.sleep(1)
        cursor = self.DBCON.cursor() 
        cursor.execute('select WEB_USER_ID from pxtsessions where ID = '+ pxt)
        result = cursor.fetchone()
        print('get_web_user: ' + str(result))
        self.web_user = result
        cursor.close()
        return self.web_user    
    
    def execute_one(self, query=None):
        time.sleep(1)
        cursor = self.DBCON.cursor() 
        cursor.execute(query)
        result = cursor.fetchone()
        #print('execute_one: ' + str(result))
        cursor.close()
        return result        