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

from report_server.common.custom_count import Rules
from report_server.sreport.tests.general import BaseReportTestCase
from django.test import TestCase
from setup import TestData


RHEL = TestData.RHEL
HA = TestData.HA
EUS = TestData.EUS
LB = TestData.LB
JBoss = TestData.JBoss
EDU = TestData.EDU
UNLIMITED = TestData.UNLIMITED
GEAR = TestData.GEAR

class RulesTestCase(BaseReportTestCase):
    def test_get_rules(self):
        r = Rules()
        rules = r.get_rules
        self.assertTrue(rules)
        
    
    def test_rules_rhel(self):
        r = Rules()
        rules = r.get_rules()
        this_test = rules[RHEL]['memtotal']
        this_expected_results = {'low_gt': 0, 'low_lt': 8388608, 'low_desc': '< 8GB', 'high_gt': 8388608, 'high_lt': 83886080, 'high_desc': '> 8GB', 'rule': '0 > 8388608; 8388608 > 83886080'}
        self.assertEqual(this_test, this_expected_results, 'results match')
    '''
    def test_update_rules(self):
        r = Rules()
        rules = r.get_rules()
        
        rules[RHEL]['memtotal'] = [0, 9388608, '< 9GB', 9388608, -1, '> 9GB' ]
        r.update_rules(rules)
        
        new_rules = r.get_rules()
        this_test = new_rules[RHEL]['memtotal']
        this_expected_results = [0, 9388608, '< 9GB', 9388608, -1, '> 9GB' ]
        self.assertEqual(this_test, this_expected_results, 'results match')
    '''
    
