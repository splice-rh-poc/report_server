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



"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from splice.common.models import ProductUsage
from django.test import TestCase
from mongoengine.connection import connect
from django.conf import settings
from logging import getLogger
from report_server.sreport.models import ReportData
from report_server.sreport.models import SpliceServer, ProductUsage
from rhic_serve.rhic_rest.models import RHIC, Account
from datetime import datetime, timedelta
from report_server.common.import_util import import_data
from report_server.common import config
from report_server.common.custom_count import Rules
from setup import TestData
from report_server.common import constants

LOG = getLogger(__name__)
config.init()
this_config = config.get_import_info()

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

class UI_TestCase(TestCase):

    
    def test_import_three(self):
        SpliceServer.drop_collection()
        ProductUsage.drop_collection()
        ReportData.drop_collection()
        fact1 = {"memory_dot_memtotal": "604836", "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        
        ss = TestData.create_splice_server("test01", "east")
        ss = TestData.create_splice_server("test02", "east")
        ss = TestData.create_splice_server("test03", "east-")
        time1 = datetime.strptime("10092012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0631", constants.mn_fmt)
        time3 = datetime.strptime("10102012:0531", constants.mn_fmt)
        time4 = datetime.strptime("10112012:0531", constants.mn_fmt)
        time5 = datetime.strptime("10112012:0631", constants.mn_fmt)
        time6 = datetime.strptime("10122012:0531", constants.mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        prod2 = products_dict[JBoss][0]
        
        TestData.create_product_usage(ss, fact1, time1, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time2, consumer=uuid, instance='mac02', products=prod)
        TestData.create_product_usage(ss, fact1, time3, consumer=uuid, instance='mac03', products=prod)
        
        TestData.create_product_usage(ss, fact1, time4, consumer=uuid, instance='mac01', products=prod2)
        TestData.create_product_usage(ss, fact1, time5, consumer=uuid, instance='mac02', products=prod2)
        TestData.create_product_usage(ss, fact1, time6, consumer=uuid, instance='mac03', products=prod)
        #run import
        results = import_data(force_import=True)
        
        #verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 6)
    
   