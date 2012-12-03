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

from rhic_serve.common.tests import BaseMongoTestCase
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


MONGO_TEST_DATABASE_NAME = 'test_%s' % settings.MONGO_DATABASE_NAME

class BaseReportTestCase(BaseMongoTestCase):

    def setUp(self):
        super(BaseReportTestCase, self).setUp()
        self.setup_database()

    def setup_database(self):
        # Disconnect from the default mongo db, and use a test db instead.
        self.disconnect_dbs()
        connection.connect(MONGO_TEST_DATABASE_NAME, 
            alias=settings.MONGO_DATABASE_NAME, tz_aware=True)
        register_connection('rhic_serve', MONGO_TEST_DATABASE_NAME)
        register_connection('checkin', MONGO_TEST_DATABASE_NAME)
        register_connection('results', MONGO_TEST_DATABASE_NAME)
        register_connection('default', MONGO_TEST_DATABASE_NAME)

        for collection in ['rhic', 'account', 'splice_server']:
            print 'importing %s collection' % collection
            call(['mongoimport', '--db', MONGO_TEST_DATABASE_NAME,
                  '-c', collection, '--file', 
                  '%s.json' % os.path.join(settings.DUMP_DIR, collection)],
                 stdout=PIPE, stderr=PIPE)


class ReportTestCase(BaseReportTestCase):
    def setUp(self):
        super(ReportTestCase, self).setUp()
        db_name = settings.MONGO_DATABASE_NAME
        self.db = connect(db_name)
        ReportData.drop_collection()
        rhel_product = TestData.create_products()
        rhel_entry = TestData.create_entry(RHEL, mem_high=True)
        rhel_entry.save()

        
    
    def test_report_data(self):
        self.setUp()
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)
    
    
    def test_generic_config_RHEL(self):
        ReportData.drop_collection()        
        entry_high = TestData.create_entry(RHEL, mem_high=True)
        entry_high.save(safe=True)

        delta=timedelta(days=1)
        start = datetime.now() - delta
        end = datetime.now() + delta
        contract_num = "3116649"
        environment = "us-east-1"
        
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)
        #test perfect match
        p = Product.objects.filter(name=RHEL)[0]
        #print(products_dict[RHEL][1])
        rhic = RHIC.objects.filter(uuid=products_dict[RHEL][1])[0]
        results_dicts = Product_Def.get_count(p, rhic, start, end, contract_num, environment, report_biz_rules)
        self.assertEqual(len(results_dicts), 1)
    
    
    def test_generic_config_RHEL_JBOSS_same_rhic(self):
        ReportData.drop_collection()
        # create 1 RHEL, 2 JBoss
        entry_high = TestData.create_entry(RHEL, mem_high=True)
        entry_high.save(safe=True)
        
        entry_high = TestData.create_entry(JBoss, socket=5)
        entry_high.save(safe=True)
        entry_low = TestData.create_entry(JBoss, socket=4 )
        entry_low.save(safe=True)

        delta=timedelta(days=1)
        start = datetime.now() - delta
        end = datetime.now() + delta
        
        environment = "us-east-1"
        
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 3)
        #test for RHEL Match
        rhic = RHIC.objects.filter(uuid=products_dict[RHEL][1])[0]
        p = Product.objects.filter(name=RHEL, sla=rhic.sla,
                                   support_level=rhic.support_level)[0]
        results_dicts = Product_Def.get_count(p, rhic, start, end, rhic.contract, environment, report_biz_rules)
        self.assertEqual(len(results_dicts), 1)
        
        #test for JBoss match
        rhic = RHIC.objects.filter(uuid=products_dict[JBoss][1])[0]
        p = Product.objects.filter(name=JBoss, sla=rhic.sla,
                                   support_level=rhic.support_level)[0]
        results_dicts = Product_Def.get_count(p, rhic, start, end, rhic.contract, environment, report_biz_rules)
        results_dicts = Product_Def.get_count(p, rhic, start, end, rhic.contract, environment, report_biz_rules)
        self.assertEqual(len(results_dicts), 2)
    
    
   
    def test_rhel_basic_results(self):
        
        delta=timedelta(days=1)
        start = datetime.now() - delta
        end = datetime.now() + delta
        contract_num = "3116649"
        environment = "us-east-1"
        
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)
        #test perfect match
        p = Product.objects.filter(name=RHEL)[0]
        rhic = RHIC.objects.filter(uuid=products_dict[RHEL][1])[0]
        results_dicts = Product_Def.get_count(p, rhic, start, end, contract_num, environment, report_biz_rules)
        self.assertEqual(len(results_dicts), 1)
    
        test_object = Product.objects.filter(name=RHEL)[0]
        test_object.name = "fail"
        try:
            results_dicts = Product_Def.get_count(test_object, rhic, start, end, contract_num, environment, report_biz_rules)
        except KeyError:
            self.assertTrue(1, 'key error appropriately found, no results returned')
        except Exception:
            self.assertTrue(0,'key error not found, error')
            
        
        # test result not found where rhic uuid does not match
        test_object =  RHIC.objects.filter(uuid="8d401b5e-2fa5-4cb6-be64-5f57386fda86")[0]
        test_object.uuid = "1234"
        results_dicts = Product_Def.get_count(p, test_object, start, end, contract_num, environment, report_biz_rules)
        self.assertFalse(results_dicts, 'no results returned')
        
        # test no results are found if usage date is not in range
        test_object = datetime.now()
        results_dicts = Product_Def.get_count(p, rhic, test_object, end, contract_num, environment, report_biz_rules)
        self.assertFalse(results_dicts, 'no results returned')
        
        test_object = start
        results_dicts = Product_Def.get_count(p, rhic, start, test_object, contract_num, environment, report_biz_rules)
        self.assertFalse(results_dicts, 'no results returned')
        
        #test if contract number is not a match
        test_object = "1234"
        results_dicts = Product_Def.get_count(p, rhic, start, end, test_object, environment, report_biz_rules)
        self.assertFalse(results_dicts, 'no results returned')
        
        #test if environment is not a match
        test_object = "env_hell"
        results_dicts = Product_Def.get_count(p, rhic, start, end, contract_num, test_object, report_biz_rules)
        self.assertFalse(results_dicts, 'no results returned')
        
        
    def test_rhel_data_range_results(self):
        contract_num = "3116649"
        environment = "us-east-1"
        search_date_start = datetime.now() - timedelta(days=11)
        search_date_end = datetime.now()
                                                     
        delta = timedelta(days=10)
        rhel = TestData.create_entry(RHEL, mem_high=True, date=(datetime.now() - delta))
        rhel.save()
        
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 2)
        
        #test that there are now two objects in the database
        p = Product.objects.filter(name=RHEL)[0]
        rhic = RHIC.objects.filter(uuid=products_dict[RHEL][1])[0]
        results_dicts = Product_Def.get_count(p, rhic, search_date_start, search_date_end, contract_num, environment, report_biz_rules)
        #lenth of list should be one per product
        self.assertEqual(len(results_dicts), 1)
        #dictionary should contain the count of checkins
        self.assertEqual(results_dicts[0]['count'], 2)
        
    def test_rhel_memory_results(self):
        contract_num = "3116649"
        environment = "us-east-1"
        end = datetime.now()
        delta=timedelta(days=1)
        start = datetime.now() - delta
        
        p = Product.objects.filter(name=RHEL)[0]
        rhic = RHIC.objects.filter(uuid=products_dict[RHEL][1])[0]
        results_dicts = Product_Def.get_count(p, rhic, start, end, contract_num, environment, report_biz_rules)
        self.assertTrue('> ' in results_dicts[0]['facts'], ' > 8GB found')
        
        rhel02 = TestData.create_entry(RHEL, mem_high=False)
        rhel02.save()
        end = datetime.now()
        
        #verify two items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 2)
        #RHEL w/ > 8GB and < 8GB memory are considered two different products
        #The result dict should have two items in the list (2 products, 1 count each)
        results_dicts = Product_Def.get_count(p, rhic, start, end, contract_num, environment, report_biz_rules)
        self.assertEqual(len(results_dicts), 2)
        
    
    def test_find_each_product(self):
        ReportData.drop_collection()
        count = 0
        for key, value in products_dict.items():
            count += 1
            entry = TestData.create_entry(key, mem_high=True)
            entry.save(safe=True)
            lookup = len(ReportData.objects.all())
            self.assertEqual(lookup, count)
            
            
        end = datetime.now()
        delta=timedelta(days=1)
        start = datetime.now() - delta
        
        for key, value in products_dict.items():
            rhic = RHIC.objects.filter(uuid=value[1])[0]
            p = Product.objects.filter(name=key, sla=rhic.sla,
                                       support_level=rhic.support_level)[0]
            results_dicts = Product_Def.get_count(p, rhic, start, end, rhic.contract, "us-east-1", report_biz_rules)
            self.assertEqual(len(results_dicts), 1)
    
    def test_hours_per_consumer(self):
        ReportData.drop_collection()
        count = 0
        for key, value in products_dict.items():
            count += 1
            entry = TestData.create_entry(key, mem_high=True)
            entry.save(safe=True)
            lookup = len(ReportData.objects.all())
            self.assertEqual(lookup, count)
        
        end = datetime.now()
        delta=timedelta(days=1)
        start = datetime.now() - delta
        
        list_of_rhics = RHIC.objects.all()
        results = hours_per_consumer(start, end, list_of_rhics )
        
        # right now products_dict RHEL and JBoss are sharing a RHIC so.. -1 on length
        self.assertEqual(len(results), (len(products_dict) -1 ), "correct number of results returned")
        results_product_list = []
        for r in results:
            self.assertEqual(r[0]['nau'], '1', "number of checkins is accurate")
            results_product_list.append(r[0]['product_name'])
        
        intersect = set(results_product_list).intersection(products_dict.keys())
        self.assertEqual(len(intersect), (len(products_dict) -1), "number of products returned in results is accurate")

    def check_product_result(self, result1, result2):   
        lookup = len(ReportData.objects.all())
        self.assertEqual(lookup, 2)
        
        end = datetime.now()
        delta=timedelta(days=1)
        start = datetime.now() - delta
        
        list_of_rhics = RHIC.objects.all()
        results = hours_per_consumer(start, end, list_of_rhics )
        
        self.assertEqual(len(results), int(result1), "correct number of results returned, 1 result per rhic")
        self.assertEqual(len(results[0]), int(result2), "correct number of products returned in result..")
    
    def test_RHEL_memory(self):
        ReportData.drop_collection()
        
        entry_high = TestData.create_entry(RHEL, mem_high=True)
        entry_high.save(safe=True)
        entry_low = TestData.create_entry(RHEL, mem_high=False)
        entry_low.save(safe=True)
        
        self.check_product_result(1, 2)
        
    def test_RHEL_memory_negative(self):
        ReportData.drop_collection()
        
        entry_high = TestData.create_entry(RHEL, mem_high=True)
        entry_high.save(safe=True)
        entry_low = TestData.create_entry(RHEL, mem_high=True, socket=12)
        entry_low.save(safe=True)
        
        self.check_product_result(1, 1)
        
    def test_JBoss_vcpu(self):
        ReportData.drop_collection()
        entry_high = TestData.create_entry(JBoss, socket=5)
        entry_high.save(safe=True)
        entry_low = TestData.create_entry(JBoss, socket=4 )
        entry_low.save(safe=True)
        
        self.check_product_result(1, 2)
    
    def test_JBoss_vcpu_negative(self):
        ReportData.drop_collection()
        entry_high = TestData.create_entry(JBoss, socket=5)
        entry_high.save(safe=True)
        entry_low = TestData.create_entry(JBoss, socket=5, mem_high=True )
        entry_low.save(safe=True)
        
        self.check_product_result(1, 1)
    
    def test_OpenShift_Gear(self):
        ReportData.drop_collection()
        entry_high = TestData.create_entry(GEAR, cpu=2, mem_high=True)
        entry_high.save(safe=True)
        entry_low = TestData.create_entry(GEAR, cpu=1, mem_high=False)
        entry_low.save(safe=True)
        
        self.check_product_result(1, 2)
    
    def test_OpenShift_Gear_negative(self):
        ReportData.drop_collection()
        entry_high = TestData.create_entry(GEAR, cpu=2, mem_high=True)
        entry_high.save(safe=True)
        entry_low = TestData.create_entry(GEAR, cpu=3, mem_high=True)
        entry_low.save(safe=True)
        
        self.check_product_result(1, 1)
    
    def test_RHEL_Host(self):
        ReportData.drop_collection()
        entry_high = TestData.create_entry(UNLIMITED, socket=3)
        entry_high.save(safe=True)
        entry_low = TestData.create_entry(UNLIMITED, socket=1 )
        entry_low.save(safe=True)
        
        self.check_product_result(1, 2)
        
    def test_RHEL_Host_negative(self):
        ReportData.drop_collection()
        entry_high = TestData.create_entry(UNLIMITED, socket=3)
        entry_high.save(safe=True)
        entry_low = TestData.create_entry(UNLIMITED, socket=3, mem_high=True )
        entry_low.save(safe=True)
        
        self.check_product_result(1, 1)
        
          
   
