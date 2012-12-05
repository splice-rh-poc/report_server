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

from datetime import datetime, timedelta
from report_server.dev.custom_count import Rules
from report_server.sreport.models import ReportData
from report_server.sreport.tests.general import BaseReportTestCase
from report_server.common.max import MaxUsage
from setup import TestData


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


class MaxReportTestCase(BaseReportTestCase):
    
    def test_report_data(self):
        """
        Basic sanity test
        """
        rhel_product = TestData.create_products()
        rhel_entry = TestData.create_entry(RHEL, mem_high=True)
        rhel_entry.save()            
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1) 
    
    def test_basic_mdu(self):
        """
        Basic test of mdu
        """
        ReportData.drop_collection()
        rhel_entry = TestData.create_entry(RHEL, mem_high=True)
        rhel_entry.save()            
        lookup = ReportData.objects.all()
        self.assertEqual(len(lookup), 1)          
        
        delta=timedelta(days=1)
        start = datetime.now() - delta
        end = datetime.now() + delta        
        
        

        filter_args = {
               "memtotal__gt": rhel_entry.memtotal - 1,
               "product": rhel_entry.product,
               "contract_id": rhel_entry.contract_id,
               "support": rhel_entry.support,
               "memtotal__lt": rhel_entry.memtotal + 1,
               "consumer_uuid": rhel_entry.consumer_uuid,
               "sla": rhel_entry.sla
        }
        
        test_dict = MaxUsage.get_MDU_MCU(start, end, filter_args, RHEL)
        result = test_dict['mdu'][1]
        self.assertEqual(result[1], 1, "correct mdu found")
        
    def test_basic_mcu(self):
            """
            Basic test of mcu
            """
            ReportData.drop_collection()
            rhel_entry = TestData.create_entry(RHEL, mem_high=True)
            rhel_entry.save()
            rhel_entry = TestData.create_entry(RHEL, instance_identifier="00:11")
            rhel_entry.save()                  
            lookup = ReportData.objects.all()
            self.assertEqual(len(lookup), 2)          
            
            delta=timedelta(days=1)
            start = datetime.now() - delta
            end = datetime.now() + delta        
            
            
    
            filter_args = {
                   "memtotal__gt": rhel_entry.memtotal - 1,
                   "product": rhel_entry.product,
                   "contract_id": rhel_entry.contract_id,
                   "support": rhel_entry.support,
                   "memtotal__lt": rhel_entry.memtotal + 1,
                   "consumer_uuid": rhel_entry.consumer_uuid,
                   "sla": rhel_entry.sla
            }
            
            test_dict = MaxUsage.get_MDU_MCU(start, end, filter_args, RHEL)
            mdu = test_dict['mdu'][1]
            mcu = test_dict['mcu'][1]
            self.assertEqual(mdu[1], 2, "correct mdu found") 
            self.assertEqual(mcu[1], 2, "correct mcu found")  
            
    def test_advanced_mcu_mdu(self):
                """
                three report data entries, each w/ unique instance_ident
                2 in the same $hour
                1 in $hour + 1
                mcu = 2 , mdu = 3
                """
                delta_day=timedelta(days=1)
                delta_hour=timedelta(hours=1)
                start = datetime.now() - delta_day
                end = datetime.now() + delta_day  
                hour_plus_1 = datetime.now() + delta_hour
                
                ReportData.drop_collection()
                rhel_entry = TestData.create_entry(RHEL,
                                                   instance_identifier="00:10")
                rhel_entry.save()
                rhel_entry = TestData.create_entry(RHEL,
                                                   instance_identifier="00:11")
                rhel_entry.save() 
                rhel_entry = TestData.create_entry(RHEL,
                                                   date=hour_plus_1,
                                                   instance_identifier="00:12")
                rhel_entry.save()                 
                lookup = ReportData.objects.all()
                self.assertEqual(len(lookup), 3)          

                filter_args = {
                       "memtotal__gt": rhel_entry.memtotal - 1,
                       "product": rhel_entry.product,
                       "contract_id": rhel_entry.contract_id,
                       "support": rhel_entry.support,
                       "memtotal__lt": rhel_entry.memtotal + 1,
                       "consumer_uuid": rhel_entry.consumer_uuid,
                       "sla": rhel_entry.sla
                }
                
                test_dict = MaxUsage.get_MDU_MCU(start, end, filter_args, RHEL)
                mdu = test_dict['mdu'][1]
                mcu = test_dict['mcu'][1]
                self.assertEqual(mdu[1], 3, "correct mdu found") 
                self.assertEqual(mcu[1], 2, "correct mcu found") 
        