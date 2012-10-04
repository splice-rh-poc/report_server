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
from splice.entitlement.models import ProductUsage


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
from sreport.models import ProductUsage, SpliceServer
from rhic_serve.rhic_rest.models import RHIC, Account
from mongoengine.queryset import QuerySet
from mongoengine import Document, StringField, ListField, DateTimeField, IntField
from datetime import datetime, timedelta
from common.products import Product_Def
from common.utils import datespan
from common.report import get_list_of_products, hours_per_consumer
from common.import_util import checkin_data
import sys


LOG = getLogger(__name__)
hr_fmt = "%m%d%Y:%H"
mn_fmt = "%m%d%Y:%H%M"
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
        

            
RHEL = "RHEL Server"
HA = "RHEL HA"
EUS = "RHEL EUS"
LB = "RHEL LB"
JBoss = "JBoss EAP"
EDU = "RHEL Server for Education"
UNLIMITED = "RHEL Server 2-socket Unlimited Guest"
GEAR = "OpenShift Gear"

products_dict={
                 RHEL: (["69"], '8d401b5e-2fa5-4cb6-be64-5f57386fda86', "rhel-server-1190457-3116649-prem-l1-l3"), 
                 HA: (["83"], 'fbbd06c6-ebed-4892-87a3-2bf17c864444', 'rhel-ha-1190457-3874444-na-standard'),
                 EUS: (["70"],'fbbd06c6-ebed-4892-87a3-2bf17c865555', 'rhel-eus-1190457-3874444-prem-l1-l3'),
                 LB: (["85"], 'fbbd06c6-ebed-4892-87a3-2bf17c866666', 'rhel-lb-1190457-3874444-prem-l1-l3'),
                 JBoss: (["183"],'ee5c9aaa-a40c-1111-80a6-ef731076bbe8', 'jboss-1111730-4582732-prem-l1-l3'),
                 EDU: (["69"], 'fbbd06c6-ebed-4892-87a3-2bf17c86e610', 'rhel-server-education-1190457-3879847-na-ss'),
                 UNLIMITED: (["69"], 'fbbd06c6-ebed-4892-87a3-2bf17c867777', 'rhel-2socket_unlimited-1190457-3874444-prem-l1-l3'),
                 GEAR: (["69", "183"], 'b0e7bd8a-0b23-4b35-86d7-52a87311a5c2', 'openshift-gear-3485301-4582732-prem-l1-l3')
                }
 
class TestData():
    
    @staticmethod
    def create_entry(product, mem_high=True, date=None, socket=4, cpu=4):
        if not date:
            date = datetime.now()
        this_hour = date.strftime(hr_fmt)
            
        row = ReportData(
                                instance_identifier = "12:31:3D:08:49:00",
                                date =  date,
                                hour = this_hour,
                                environment = "us-east-1",
                                splice_server = "splice-server-1.spliceproject.org"
                                )
        
        for key, value in products_dict.items():
            if product == key:
                rhic = RHIC.objects.filter(uuid=value[1])[0]
                row['product_name']=key
                row['product']=value[0]
                row['consumer_uuid']=value[1]
                row['consumer']=value[2]
                row['contract_id']=rhic.contract
                row['sla']=rhic.sla
                row['support']=rhic.support_level
                row['contract_use']="20"
                row['cpu_sockets'] = socket
                row['cpu'] = cpu
                
        
        if mem_high:
            row['memtotal'] = 16048360
            return row
        else:
            row['memtotal'] = 640
            return row
        
        

        
       
        
    
    @staticmethod    
    def create_products():
        #currently we rely on specific rhics to be created by the generate_product_usage script in splice-server/playpen
        # assert that appears to be sane..
        
        num = RHIC.objects.all().count()
        if num != 9:
            raise Exception('rhics in rhic_serve db may not be valid')
            
        
        for key, value in products_dict.items():
            #print('create_product', key)
            rhic = RHIC.objects.filter(uuid=value[1])[0]
            contract_num = rhic.contract
            #print('contract_num', contract_num)
            #print('account_id', rhic.account_id)
            list_of_products = get_list_of_products(rhic.account_id, contract_num)
                    
            products_contract = [(prod.name) for prod in list_of_products]
            intersect = set(products_contract).intersection(set(rhic.products))
            #print(intersect)
            if len(intersect) < 1:
                raise Exception('rhics and account/contracts in rhic_serve db may not be valid')
                
            
            for p in list_of_products:
                #print p.name
                if p.name == key:
                    row = Product(
                                  quantity = p.quantity,
                                  support_level = p.support_level,
                                  sla = p.sla,
                                  name=p.name,
                                  engineering_ids=p.engineering_ids
                                  )
                    row.save()
            
    @staticmethod
    def create_rhic():
        rhic = {
                    'uuid': '1001',
                    'name': 'test_rhic',
                    'account_id': '1001',
                    'contract': '1',
                    'support_level': 'l1-l3',
                    'sla': 'prem',
                    'products': [RHEL, HA, EDU, EUS, LB, JBoss, GEAR ],
                    'engineering_ids': ["69", "83", "70", "85", "183"]
                    }
                    
        RHIC.objects.get_or_create(rhic)
        
    @staticmethod
    def create_splice_server(hostname='splice01.example.com', environment="east"):
        ss = SpliceServer(
                  uuid=hostname,
                  description=hostname,
                  hostname=hostname,
                  environment=environment
                )
        ss.save()
        return ss
        
    @staticmethod
    def create_product_usage(splice_server, facts, cdate, consumer='consumer01', instance='ident01', products=['69']):
        pu = ProductUsage(
             consumer=consumer,
             splice_server=splice_server,
             instance_identifier=instance,
             allowed_product_info=products,
             facts=facts,
             date=cdate
             )
        pu.save(cascade=True)
    
class ReportTestCase(TestCase):
    def setUp(self):
        db_name = settings.MONGO_DATABASE_NAME_RESULTS
        self.db = connect(db_name)
        ReportData.drop_collection()
        rhel_product = TestData.create_products()
        rhel_entry = TestData.create_entry(RHEL, mem_high=True)
        rhel_entry.save()

        
         
    def test_report_data(self):
        self.setUp()
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)
     
    def test_rhel_basic_results(self):
        
        delta=timedelta(days=1)
        start = datetime.now() - delta
        end = datetime.now() + delta
        contract_num = "3116649"
        environment = "us-east-1"
        
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)
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
        p = Product.objects.filter(name="RHEL Server")[0]
        rhic = RHIC.objects.filter(uuid="8d401b5e-2fa5-4cb6-be64-5f57386fda86")[0]
        results_dicts = Product_Def.get_product_match(p, rhic, search_date_start, search_date_end, contract_num, environment)
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
        
        p = Product.objects.filter(name="RHEL Server")[0]
        rhic = RHIC.objects.filter(uuid="8d401b5e-2fa5-4cb6-be64-5f57386fda86")[0]
        results_dicts = Product_Def.get_product_match(p, rhic, start, end, contract_num, environment)
        self.assertTrue('> ' in results_dicts[0]['facts'], ' > 8GB found')
        
        rhel02 = TestData.create_entry(RHEL, mem_high=False)
        rhel02.save()
        end = datetime.now()
        
        #verify two items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 2)
        #RHEL w/ > 8GB and < 8GB memory are considered two different products
        #The result dict should have two items in the list (2 products, 1 count each)
        results_dicts = Product_Def.get_product_match(p, rhic, start, end, contract_num, environment)
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
            #print(key)
            p = Product.objects.filter(name=key)[0]
            #print(p.name)

            rhic = RHIC.objects.filter(uuid=value[1])[0]
            #print(rhic.uuid)
            #print(rhic.contract)
            results_dicts = Product_Def.get_product_match(p, rhic, start, end, rhic.contract, "us-east-1")
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
        
        self.assertEqual(len(results), len(products_dict), "correct number of results returned")
        results_product_list = []
        for r in results:
            self.assertEqual(r[0]['checkins'], '1', "number of checkins is accurate")
            results_product_list.append(r[0]['product_name'])
        
        intersect = set(results_product_list).intersection(products_dict.keys())
        self.assertEqual(len(intersect), len(products_dict), "number of products returned in results is accurate")

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
        
        
    
    
    #def create_product_usage(splice_server, facts, cdate, consumer='consumer01', instance='ident01', products=['69']):
    def test_import(self):
        SpliceServer.drop_collection()
        ProductUsage.drop_collection()
        ReportData.drop_collection()
        fact1 = {"memory_dot_memtotal": "604836", "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        
        ss = TestData.create_splice_server("test01", "east")
        time = datetime.strptime("10102012:05", hr_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        pu = TestData.create_product_usage(ss, fact1, time, consumer=uuid, instance='mac01', products=prod)
        #run import
        results = checkin_data()
        
        #verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)
    
    def test_import_dup(self):
        SpliceServer.drop_collection()
        ProductUsage.drop_collection()
        ReportData.drop_collection()
        fact1 = {"memory_dot_memtotal": "604836", "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        
        ss = TestData.create_splice_server("test01", "east")
        time = datetime.strptime("10102012:0530", mn_fmt)
        time2 = datetime.strptime("10102012:0531", mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        pu = TestData.create_product_usage(ss, fact1, time, consumer=uuid, instance='mac01', products=prod)
        pu = TestData.create_product_usage(ss, fact1, time2, consumer=uuid, instance='mac01', products=prod)
        #run import
        results = checkin_data()
        
        #verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)
    
    def test_import_three(self):
        SpliceServer.drop_collection()
        ProductUsage.drop_collection()
        ReportData.drop_collection()
        fact1 = {"memory_dot_memtotal": "604836", "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        
        ss = TestData.create_splice_server("test01", "east")
        time = datetime.strptime("10102012:0530", mn_fmt)
        time2 = datetime.strptime("10102012:0631", mn_fmt)
        time3 = datetime.strptime("10102012:0531", mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(ss, fact1, time, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time2, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time3, consumer=uuid, instance='mac01', products=prod)
        #run import
        results = checkin_data()
        
        #verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 2)
    
    def test_import_four(self):
        SpliceServer.drop_collection()
        ProductUsage.drop_collection()
        ReportData.drop_collection()
        fact1 = {"memory_dot_memtotal": "604836", "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        
        ss = TestData.create_splice_server("test01", "east")
        time = datetime.strptime("10102012:0530", mn_fmt)
        time2 = datetime.strptime("10102012:0631", mn_fmt)
        time3 = datetime.strptime("10102012:0531", mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(ss, fact1, time, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time2, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time3, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time3, consumer=uuid, instance='mac02', products=prod)
        #run import
        results = checkin_data()
        
        #verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 3)
    
    def test_import_change_rhics(self):
        SpliceServer.drop_collection()
        ProductUsage.drop_collection()
        ReportData.drop_collection()
        fact1 = {"memory_dot_memtotal": "604836", "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        
        ss = TestData.create_splice_server("test01", "east")
        time = datetime.strptime("10102012:0530", mn_fmt)
        time2 = datetime.strptime("10102012:0631", mn_fmt)
        time3 = datetime.strptime("10102012:0531", mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(ss, fact1, time, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time2, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time3, consumer=uuid, instance='mac01', products=prod)
        uuid = products_dict[EDU][1]
        TestData.create_product_usage(ss, fact1, time3, consumer=uuid, instance='mac01', products=prod)
        #run import
        results = checkin_data()
        
        #verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 3)
        
    
    
    