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
import time
from report_server.common.import_util import import_data
from report_server.common import config
from report_server.common.custom_count import Rules
from setup import TestData
from report_server.common import constants
import random, string

LOG = getLogger(__name__)
this_config = config.get_import_info()




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
        ss1 = TestData.create_splice_server("test01", "east")
        
        uuid_rhel_jboss = products_dict[RHEL][1]
        prod_rhel = products_dict[RHEL][0]
        prod_jboss = products_dict[JBoss][0]
        
        uuid_ha = products_dict[HA][1]
        prod_ha = products_dict[HA][0]
        
        uuid_edu = products_dict[EDU][1]
        prod_edu = products_dict[EDU][0]
        
        
        
        
        
        now = datetime.now()
        delta_day = timedelta(days=4)
        delta_hour = timedelta(days=3)
        
        
        for i in range(1,10):
            this_time = now - (delta_hour * i)
            create_set_of_usage(prod_rhel, uuid_rhel_jboss, getTimes(this_time), ss1, 7)
            
        for i in range(1,10):
            this_time = now - (delta_hour * i)
            create_set_of_usage(prod_jboss, uuid_rhel_jboss, getTimes(this_time), ss1, 4)
        
        for i in range(1,4):
            this_time = now - (delta_hour * i)
            create_set_of_usage(prod_ha, uuid_ha, getTimes(this_time), ss1, 7)
            
        for i in range(5,10):
            this_time = now - (delta_hour * i)
            create_set_of_usage(prod_edu, uuid_edu, getTimes(this_time), ss1, 5)
        #run import
        results = import_data(force_import=True)
        
        
        #verify 1 items in db
        lookup = ReportData.objects.all()
        #print(len(lookup))
        
        
def getTimes(start):
            delta_day = timedelta(days=1)
            minus_one = start - (delta_day * 1)
            minus_one = minus_one.strftime(constants.month_day_year_fmt)
            timelist = []
            delta_hour = timedelta(hours=1)
            time1 = datetime.strptime(minus_one + ":0130", constants.mn_fmt)
            time2 = time1 + delta_hour
            time3 = time1 + (delta_hour * 2)
            time4 = time1 + (delta_hour * 6)
            time5 = time1 + (delta_hour * 7)
            time6 = time1 + (delta_hour * 10)
            
            time7 = time1 + (delta_hour * 12)
            time8 = time7 + delta_hour
            time9 = time7 + (delta_hour * 2)
            time10 = time7 + (delta_hour * 8)
            time11 = time7 + (delta_hour * 9)
            time12 = time7 + (delta_hour * 12)
            
            timelist = [time1, time2, time3, time4, time5, time6, time7, time8, time9, time10, time11, time12]
            return timelist
        
def create_set_of_usage(prod, uuid, list_of_times, splice_server, iterate_num):
            fact1 = {"memory_dot_memtotal": "604836", "lscpu_dot_cpu_socket(s)": "1", "lscpu_dot_cpu(s)": "1"}
        
            
            for i in range(iterate_num):
                lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(10)]
                rand = "".join(lst)
                #print rand
            
                
                mac01 = '00:24:7E:69:5C:57-03:54:' + rand
                mac02 = '00:DF:FD:45:6V:54-05:34:' + rand
                mac03 = '34:EF:GR:34:4C:4T-34:45:' + rand
                mac04 = 'RT:ER:G4:24:C6:47-38:49:' + rand
                mac05 = 'Z4:EF:ZR:34:XC:4Z-34:43:' + rand
                
                
                
                #MCU =2 MDU =3 
                TestData.create_product_usage(splice_server, fact1, list_of_times[0], consumer=uuid, instance=mac01, products=prod)
                TestData.create_product_usage(splice_server, fact1, list_of_times[0], consumer=uuid, instance=mac02, products=prod)
                TestData.create_product_usage(splice_server, fact1, list_of_times[1], consumer=uuid, instance=mac03, products=prod)
        
        
                #MCU=3 MDU =5
                TestData.create_product_usage(splice_server, fact1, list_of_times[8], consumer=uuid, instance=mac01, products=prod)
                TestData.create_product_usage(splice_server, fact1, list_of_times[9], consumer=uuid, instance=mac02, products=prod)
                TestData.create_product_usage(splice_server, fact1, list_of_times[9], consumer=uuid, instance=mac03, products=prod)
                TestData.create_product_usage(splice_server, fact1, list_of_times[9], consumer=uuid, instance=mac04, products=prod)
                TestData.create_product_usage(splice_server, fact1, list_of_times[11], consumer=uuid, instance=mac01, products=prod)
    
   