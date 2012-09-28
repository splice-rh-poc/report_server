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

from django.test import TestCase
from mongoengine.connection import connect, disconnect
from django.conf import settings
from logging import getLogger
from sreport.models import ReportData, MyQuerySet
from rhic_serve.rhic_rest.models import RHIC
from mongoengine.queryset import QuerySet
from mongoengine import Document, StringField, ListField, DateTimeField, IntField
from datetime import datetime, timedelta
from common.products import Product_Def


LOG = getLogger(__name__)

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

class ReportData(ReportData):
    db_name = settings.MONGO_DATABASE_NAME_RESULTS
    meta = {'queryset_class': MyQuerySet}

class Product(Document):

    support_level_choices = {
        'l1-l3': 'L1-L3',
        'l3': 'L3-only',
        'ss': 'SS',
    }

    sla_choices = {
        'std': 'Standard',
        'prem': 'Premium',
        'na': 'N/A',
    }

    # Product name
    name = StringField(required=True)
    # Unique product identifier
    engineering_ids = ListField(required=True)
    # Quantity 
    quantity = IntField(required=True)
    # Product support level
    support_level = StringField(required=True, choices=support_level_choices.keys())
    # Product sla
    sla = StringField(required=True, choices=sla_choices.keys())
    


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
    def test_basic_addition_false(self):
        self.assertNotEquals(1 + 1, 3)

class MongoTestCase(TestCase):
    """
    TestCase class that clear the collection between the tests
    """
    db_name = settings.MONGO_DATABASE_NAME_RESULTS
    def __init__(self, methodName='runtest'):
        super(MongoTestCase, self).__init__(methodName)
        disconnect()
        self.db = connect(self.db_name)
        self.drop_database_and_reconnect()
    
    def _post_teardown(self):
        super(MongoTestCase, self)._post_teardown()
        self.drop_database_and_reconnect(reconnect=False)

    def drop_database_and_reconnect(self, reconnect=True):
        disconnect()
        self.db.drop_database(self.db_name)
        # Mongoengine sometimes doesn't recreate unique indexes
        # in between test runs, adding the below 'reset' to fix this
        # https://github.com/hmarr/mongoengine/issues/422
        QuerySet._reset_already_indexed()
        if reconnect:
            self.db = connect(self.db_name)
    
class MongoTestsTestCase(MongoTestCase):

    def test_mongo_cleanup_is_working(self):
        class MongoTestEntry(Document):
            uuid = StringField(required=True, unique=True)
        m = MongoTestEntry(uuid="new_entry")
        m.save()
        lookup = MongoTestEntry.objects()
        self.assertEqual(len(lookup), 1)
        self.drop_database_and_reconnect()
        lookup = MongoTestEntry.objects()
        self.assertEqual(len(lookup), 0)
        

            
    
class TestData():
    def create_rhel_entry(self):
        this_date = datetime.now()
        
        rhel01_product = Product(
                                 name = "RHEL Server",
                                 engineering_ids = ["69"],
                                 quantity = "20",
                                 support_level = "l1-l3",
                                 sla = "prem"
                                 )
        rhel01_product.save()
        
        rhel01 = ReportData(
                            instance_identifier = "12:31:3D:08:49:00",
                            consumer_uuid = "8d401b5e-2fa5-4cb6-be64-5f57386fda86",
                            consumer = "rhel-server-1190457-3116649-prem-l1-l3",
                            product=["69"],
                            product_name = "RHEL Server",
                            date =  this_date,
                            sla = "prem",
                            support = "l1-l3",
                            contract_id = "3116649",
                            contract_use = "20", 
                            hour = "07012012:00",
                            memtotal = 16048360,
                            cpu_sockets = 4,
                            environment = "us-east-1",
                            splice_server = "splice-server-1.spliceproject.org"
                            )
        rhel01.save()
    
class ReportTestCase(TestCase):
    def setUp(self):
        db_name = settings.MONGO_DATABASE_NAME_RESULTS
        self.db = connect(db_name)
        ReportData.drop_collection()
        TestData().create_rhel_entry()
        
         
    def test_report_data(self):
        lookup = ReportData.objects()
        self.assertEqual(len(lookup), 1)
     
    def test_rhel_basic_results(self):
        end = datetime.now()
        delta=timedelta(days=1)
        start = datetime.now() - delta
        contract_num = "3116649"
        environment = "us-east-1"
        
        #test perfect match
        p = Product.objects.filter(name="RHEL Server")[0]
        rhic = RHIC.objects.filter(uuid="8d401b5e-2fa5-4cb6-be64-5f57386fda86")[0]
        results_dicts = Product_Def.get_product_match(p, rhic, start, end, contract_num, environment)
        self.assertEqual(len(results_dicts), 1)
        
        #test result not found if name does not match
        test_object = Product.objects.filter(name="RHEL Server")[0]
        test_object.name = "fail"
        results_dicts = Product_Def.get_product_match(test_object, rhic, start, end, contract_num, environment)
        self.assertFalse(results_dicts, 'no results returned')
        
        # test result not found where rhic uuid does not match
        test_object =  RHIC.objects.filter(uuid="8d401b5e-2fa5-4cb6-be64-5f57386fda86")[0]
        test_object.uuid = "1234"
        results_dicts = Product_Def.get_product_match(p, test_object, start, end, contract_num, environment)
        self.assertFalse(results_dicts, 'no results returned')
        
        # test no results are found if usage date is not in range
        test_object = datetime.now()
        results_dicts = Product_Def.get_product_match(p, rhic, test_object, end, contract_num, environment)
        self.assertFalse(results_dicts, 'no results returned')
        
        test_object = start
        results_dicts = Product_Def.get_product_match(p, rhic, start, test_object, contract_num, environment)
        self.assertFalse(results_dicts, 'no results returned')
        
        #test if contract number is not a match
        test_object = "1234"
        results_dicts = Product_Def.get_product_match(p, rhic, start, end, test_object, environment)
        self.assertFalse(results_dicts, 'no results returned')
        
        #test if environment is not a match
        test_object = "env_hell"
        results_dicts = Product_Def.get_product_match(p, rhic, start, end, contract_num, test_object)
        self.assertFalse(results_dicts, 'no results returned')
        
        
    