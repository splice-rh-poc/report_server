from dev.custom_count import Rules
from django.test import TestCase
from sreport.models import ReportDataDaily, ProductUsage
from common.import_util import import_data
from sreport.models import SpliceServer
from rhic_serve.rhic_rest.models import RHIC, Account
from datetime import datetime, timedelta
from common.products import Product_Def
from common.report import hours_per_consumer
from dev.custom_count import Rules
from setup import TestData, Product
from common import constants


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

class MDUTestCase(TestCase):
   
    def test_change_rules(self):
        r = Rules()
        rules = report_biz_rules
        
        rules[RHEL]['calculation'] = 'daily'
        r.update_rules(rules)
        
        new_rules = r.get_rules()
        this_test = new_rules[RHEL]['calculation']
        this_expected_results = 'daily'
        self.assertEqual(this_test, this_expected_results, 'results match')
        
    def test_daily_RHEL(self):
        ReportDataDaily.drop_collection()        
        entry_high = TestData.create_entry(RHEL, mem_high=True)
        entry_high.save(safe=True)

        delta=timedelta(days=1)
        start = datetime.now() - delta
        end = datetime.now() + delta
        contract_num = "3116649"
        environment = "us-east-1"
        
        lookup = ReportDataDaily.objects.all()
        self.assertEqual(len(lookup), 1)
        #test perfect match
        p = Product.objects.filter(name="RHEL Server")[0]
        rhic = RHIC.objects.filter(uuid="8d401b5e-2fa5-4cb6-be64-5f57386fda86")[0]
        results_dicts = Product_Def.get_product_match(p, rhic, start, end, contract_num, environment, report_biz_rules)
        self.assertEqual(len(results_dicts), 1)
        
    def test_import_dup(self):
        SpliceServer.drop_collection()
        ProductUsage.drop_collection()
        ReportDataDaily.drop_collection()
        fact1 = {"memory_dot_memtotal": "604836", "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        
        ss = TestData.create_splice_server("test01", "east")
        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0631", constants.mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(ss, fact1, time, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time2, consumer=uuid, instance='mac01', products=prod)
        #run import
        results = import_data(checkin_interval=24)
        
        #verify 1 items in db
        lookup = ReportDataDaily.objects.all()
        self.assertEqual(len(lookup), 1)
        
    def test_import_two_days_with_dupe(self):
        SpliceServer.drop_collection()
        ProductUsage.drop_collection()
        ReportDataDaily.drop_collection()
        fact1 = {"memory_dot_memtotal": "604836", "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        
        ss = TestData.create_splice_server("test01", "east")
        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0631", constants.mn_fmt)
        time3 = datetime.strptime("10112012:0001", constants.mn_fmt)
        time4 = datetime.strptime("10112012:2359", constants.mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(ss, fact1, time, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time2, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time3, consumer=uuid, instance='mac01', products=prod)
        TestData.create_product_usage(ss, fact1, time4, consumer=uuid, instance='mac01', products=prod)
        #run import
        results = import_data(checkin_interval=24)
        
        #verify 1 items in db
        lookup = ReportDataDaily.objects.all()
        self.assertEqual(len(lookup), 2)
    