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
from datetime import datetime, timedelta
from django.test import TestCase
from django.conf import settings
from logging import getLogger
from mongoengine.connection import connect
from report_server.sreport.models import ReportData
from report_server.sreport.models import SpliceServer, ProductUsage
from report_server.common.import_util import import_data
from report_server.common import config
from report_server.common.biz_rules import Rules
from report_server.common import constants
from report_server.sreport.tests.general import BaseMongoTestCase
from rhic_serve.rhic_rest.models import RHIC, Account
from setup import TestData
from splice.common.models import ProductUsage

LOG = getLogger(__name__)


'''
Currently the unit tests required that the rhic_serve database has been
populated w/ the sample-load.py script
This can be found @rhic_serve/playpen/sample-load.py
Example: python sample-load.py Splice-RHIC-Sample-Data.csv Splice-Product-Definitions.csv

Although the product usage data from the is not used from the splice-server's
generate_usage_data.py script, the generated RHIC's are used.
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


class ReportImportTestCase(BaseMongoTestCase):

    def setUp(self):
        super(ReportImportTestCase, self).setUp()
        #rhel_product = TestData.create_products()
        #rhel_entry = TestData.create_entry(RHEL, mem_high=True)
        #rhel_entry.save()
        self.ss = SpliceServer.objects.get(hostname="test01")

    def test_import(self):
        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}

        time = datetime.strptime("10102012:05", constants.hr_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        pu = TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                           instance='mac01', products=prod)
        # run import
        results = import_data(force_import=True)

        # verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)

    def test_import_dup(self):
        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}

        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0531", constants.mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        pu = TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                           instance='mac01', products=prod)
        pu = TestData.create_product_usage(self.ss, fact1, time2, 
                                           consumer=uuid, instance='mac01',
                                           products=prod)
        # run import
        results = import_data(force_import=True)

        # verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)

    def test_import_three(self):
        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}

        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0631", constants.mn_fmt)
        time3 = datetime.strptime("10102012:0531", constants.mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time2, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time3, consumer=uuid,
                                      instance='mac01', products=prod)
        # run import
        results = import_data(force_import=True)

        # verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 2)

    def test_import_four(self):

        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}

        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0631", constants.mn_fmt)
        time3 = datetime.strptime("10102012:0531", constants.mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time2, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time3, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time3, consumer=uuid,
                                      instance='mac02', products=prod)
        # run import
        results = import_data(force_import=True)

        # verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 3)

    def test_import_change_rhics(self):
        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}

        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0631", constants.mn_fmt)
        time3 = datetime.strptime("10102012:0531", constants.mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time2, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time3, consumer=uuid,
                                      instance='mac01', products=prod)
        uuid = products_dict[EDU][1]
        TestData.create_product_usage(self.ss, fact1, time3, consumer=uuid,
                                      instance='mac01', products=prod)
        # run import
        results = import_data(force_import=True)

        # verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 3)

    def import_bulk_load_base(self, items_to_load):
        # turn off bulk load option

        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        timedelt = timedelta(hours=1)
        uuid = products_dict[RHEL][1]
        instance = 'mac01'
        products = products_dict[RHEL][0]
        bulk_load = {}
        for i in range(items_to_load):
            time += timedelt
            this_hash = hash(
                str(uuid) + str(instance) + str(time) + str(products))
            td = TestData.create_product_usage(self.ss, fact1, time, consumer=uuid, instance=instance, products=products, save=False)
            bulk_load[this_hash] = td
        # print(len(bulk_load))
        my_list = []
        for key, value in bulk_load.items():
            my_list.append(value)

        timer_start = datetime.now()
        results = import_data(product_usage=my_list, force_import=True)
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), items_to_load)

        timer_stop = datetime.now()
        #print('\n')
        #print('**** use_bulk_load =' + ' ' + str(timer_stop - timer_start))

    def test_import_interval_2(self):
        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}

        time = datetime.strptime("10102012:05", constants.hr_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        pu = TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                           instance='mac01', products=prod)
        # run import
        results = import_data(checkin_interval=2, force_import=True)

        # verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 2)

    def test_import_interval_2_with_real_dupe_simple(self):

        # interval set at 2... for each checkin two total checkins will be created.
        # 2 real checkins should be created.. and 2 dupes..
        # A second real checkin occurs but is a dupe.

        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}

        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0539", constants.mn_fmt)

        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time2, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                      instance='mac02', products=prod)
        TestData.create_product_usage(self.ss, fact1, time2, consumer=uuid,
                                      instance='mac02', products=prod)
        # run import
        results = import_data(checkin_interval=2, force_import=True)

        # verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 4)

    def test_import_interval_2_with_real_dupe01(self):

        # interval set at 2... for each checkin two total checkins will be created.
        # 2 real checkins should be created.. and 2 dupes..
        # A second real checkin occurs but one hour of each checkin is a dupe.
        # Total should be six

        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}

        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0639", constants.mn_fmt)

        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time2, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                      instance='mac02', products=prod)
        TestData.create_product_usage(self.ss, fact1, time2, consumer=uuid,
                                      instance='mac02', products=prod)
        # run import
        results = import_data(checkin_interval=2, force_import=True)

        # verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 6)

    def test_import_interval_2_with_real_dupe02(self):

        fact1 = {"memory_dot_memtotal": "604836",
                 "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}

        time = datetime.strptime("10102012:0530", constants.mn_fmt)
        time2 = datetime.strptime("10102012:0731", constants.mn_fmt)
        time3 = datetime.strptime("10102012:0831", constants.mn_fmt)
        uuid = products_dict[RHEL][1]
        prod = products_dict[RHEL][0]
        TestData.create_product_usage(self.ss, fact1, time, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time2, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time3, consumer=uuid,
                                      instance='mac01', products=prod)
        TestData.create_product_usage(self.ss, fact1, time3, consumer=uuid,
                                      instance='mac02', products=prod)
        # run import
        results = import_data(checkin_interval=2, force_import=True)

        # verify 1 items in db
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 7)

    def test_import_bulk_load_100(self):
        self.import_bulk_load_base(100)

    '''
    def test_import_bulk_load_200(self):
        self.import_bulk_load_base(200)
        self.import_bulk_load_base(200, use_bulk_load=True)
        #print('debug')

    def test_import_bulk_load_250(self):
        self.import_bulk_load_base(250)
        self.import_bulk_load_base(250, use_bulk_load=True)
        #print('debug')
    '''
    def test_import_bulk_load_1000(self):
        self.import_bulk_load_base(1000)

    '''
    def test_import_bulk_load_1333(self):
        self.import_bulk_load_base(1333)
        self.import_bulk_load_base(1333, use_bulk_load=True)

    def test_import_bulk_load_6001(self):
        self.import_bulk_load_base(6001)
        self.import_bulk_load_base(6001, use_bulk_load=True)
    '''
