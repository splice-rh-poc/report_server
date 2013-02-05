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


from subprocess import call, PIPE
import os
from datetime import datetime, timedelta
from logging import getLogger

from django.conf import settings
from django.test import TestCase
from mongoengine.connection import connect
from mongoengine import connection, register_connection

from rhic_serve.common.tests import BaseMongoTestCase, MongoApiTestCase
from rhic_serve.rhic_rest.models import RHIC, Account
from splice.common.models import ProductUsage

from report_server.common.biz_rules import Rules
from report_server.common import config
from report_server.common import constants
from report_server.common.products import Product_Def
from report_server.common.report import hours_per_consumer
from report_server.sreport.models import ReportData
from report_server.sreport.models import SpliceServer
from report_server.sreport.tests.setup import TestData, Product


LOG = getLogger(__name__)
#this_config = config.get_import_info()
ss = SpliceServer

'''
Currently the unit tests required that the rhic_serve database has been populated w/ the sample-load.py script
This can be found @rhic_serve/playpen/sample-load.py
Example: python sample-load.py Splice-RHIC-Sample-Data.csv Splice-Product-Definitions.csv

Although the product usage data from the is not used from the splice-server's generate_usage_data.py script, the generated RHIC's are used.
It is also a current requirement to load RHIC's.
This script can be found @splice-server/playpen/generate_usage_data.py
Example: PYTHONPATH=~/workspace/rhic_serve/ DJANGO_SETTINGS_MODULE='dev.settings' ./generate_usage_data.py -n 1

Example of running these unit tests from $checkout/src
#python manage.py test sreport --settings=dev.settings -v 3

'''

RHEL = TestData.RHEL
HA = TestData.HA
EUS = TestData.EUS
LB = TestData.LB
JBoss = TestData.JBoss
EDU = TestData.EDU
UNLIMITED = TestData.UNLIMITED
GEAR = TestData.GEAR

products_dict = TestData.PRODUCTS_DICT


rules = Rules()
report_biz_rules = rules.get_rules()


#MONGO_TEST_DATABASE_NAME = 'test_%s' % settings.MONGO_DATABASE_NAME
rhic_serve = settings.MONGO_DATABASE_NAME_RHICSERVE 
checkin = settings.MONGO_DATABASE_NAME_CHECKIN
report = settings.MONGO_DATABASE_NAME

class BaseReportTestCase(BaseMongoTestCase):

    def setUp(self):
        super(BaseReportTestCase, self).setUp()
        self.setup_database()

    def setup_database(self):
        # Disconnect from the default mongo db, and use a test db instead.
        self.disconnect_dbs()
        connection.connect(report, 
            alias=report, tz_aware=True)
        register_connection(rhic_serve, rhic_serve)
        register_connection(checkin, checkin)
        register_connection(report, report)
        register_connection('default', rhic_serve)

        for collection in ['rhic', 'account']:
            #print 'importing %s collection' % collection
            call(['mongoimport', '--db', 'rhic_serve',
                  '-c', collection, '--file', 
                  '%s.json' % os.path.join(settings.DUMP_DIR, collection)],
                 stdout=PIPE, stderr=PIPE)
        
        for collection in ['splice_server']:
            #print 'importing %s collection' % collection
            call(['mongoimport', '--db', 'checkin',
                  '-c', collection, '--file', 
                  '%s.json' % os.path.join(settings.DUMP_DIR, collection)],
                 stdout=PIPE, stderr=PIPE)

class MongoApiTestCase(MongoApiTestCase):

    username = 'shadowman@redhat.com'
    password = 'shadowman@redhat.com'

    def login(self):
        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

    def post(self, url, data, code=202):
        self.login()
        content_type = 'application/json'
        response = self.client.post(url, data, content_type)
        self.assertEquals(response.status_code, code)
        self.client.logout()
        return response

    def get(self, url):
        self.login()
        content_type = 'application/json'
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.client.logout()
        return response

    def delete(self, url):
        self.login()
        content_type = 'application/json'
        response = self.client.delete(url)
        self.assertEquals(response.status_code, 204)
        self.client.logout()
        return response

    def patch(self, url, data):
        self.login()
        content_type = 'application/json'
        response = self.client.patch(url, data, content_type)
        self.assertEquals(response.status_code, 202)
        self.client.logout()
        return response


