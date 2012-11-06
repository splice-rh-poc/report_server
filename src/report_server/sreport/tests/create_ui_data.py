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
        time1 = datetime.strptime("10102012:0130", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0231", constants.mn_fmt)
        time3 = datetime.strptime("10102012:0331", constants.mn_fmt)
        time4 = datetime.strptime("10102012:0931", constants.mn_fmt)
        time5 = datetime.strptime("10102012:1031", constants.mn_fmt)
        time6 = datetime.strptime("10102012:2331", constants.mn_fmt)
        
        time7 = datetime.strptime("10142012:0130", constants.mn_fmt)
        time8 = datetime.strptime("10142012:0231", constants.mn_fmt)
        time9 = datetime.strptime("10142012:0331", constants.mn_fmt)
        time10 = datetime.strptime("10142012:0931", constants.mn_fmt)
        time11 = datetime.strptime("10142012:1031", constants.mn_fmt)
        time12 = datetime.strptime("10142012:2331", constants.mn_fmt)
        
        mac01 = '00:24:7E:69:5C:57-03:54:34:23:23:65:'
        mac02 = '00:DF:FD:45:6V:54-05:34:00:24:34:01:'
        mac03 = '34:EF:GR:34:4C:4T-34:45:55:76:65:32:'
        mac04 = 'RT:ER:G4:24:C6:47-38:49:85:77:85:02:'
        mac05 = 'Z4:EF:ZR:34:XC:4Z-34:43:54:73:25:22:'
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        prod2 = products_dict[JBoss][0]
        
        #MCU =2 MDU =3 
        TestData.create_product_usage(ss, fact1, time1, consumer=uuid, instance=mac01, products=prod)
        TestData.create_product_usage(ss, fact1, time1, consumer=uuid, instance=mac02, products=prod)
        TestData.create_product_usage(ss, fact1, time2, consumer=uuid, instance=mac03, products=prod)

        #MCU=3 MDU =5
        TestData.create_product_usage(ss, fact1, time4, consumer=uuid, instance=mac01, products=prod2)
        TestData.create_product_usage(ss, fact1, time4, consumer=uuid, instance=mac02, products=prod2)
        TestData.create_product_usage(ss, fact1, time5, consumer=uuid, instance=mac03, products=prod2)
        TestData.create_product_usage(ss, fact1, time4, consumer=uuid, instance=mac04, products=prod2)
        TestData.create_product_usage(ss, fact1, time5, consumer=uuid, instance=mac05, products=prod2)
        
        
        #MCU =2 MDU =3 
        TestData.create_product_usage(ss, fact1, time6, consumer=uuid, instance=mac01, products=prod2)
        TestData.create_product_usage(ss, fact1, time6, consumer=uuid, instance=mac02, products=prod2)
        TestData.create_product_usage(ss, fact1, time8, consumer=uuid, instance=mac03, products=prod2)

        #MCU=3 MDU =5
        TestData.create_product_usage(ss, fact1, time9, consumer=uuid, instance=mac01, products=prod)
        TestData.create_product_usage(ss, fact1, time10, consumer=uuid, instance=mac02, products=prod)
        TestData.create_product_usage(ss, fact1, time10, consumer=uuid, instance=mac03, products=prod)
        TestData.create_product_usage(ss, fact1, time10, consumer=uuid, instance=mac04, products=prod)
        TestData.create_product_usage(ss, fact1, time12, consumer=uuid, instance=mac01, products=prod)
        
    
        #run import
        results = import_data(force_import=True)
        
        #verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 16)
    
   