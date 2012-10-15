from dev.custom_count import Rules
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

class RulesTestCase(TestCase):
    def test_get_rules(self):
        r = Rules()
        rules = r.get_rules
        self.assertTrue(rules)
        
    
    def test_rules_rhel(self):
        r = Rules()
        rules = r.get_rules()
        this_test = rules[RHEL]['memtotal']
        this_expected_results = [0, 8388608, '< 8GB', 8388608, -1, '> 8GB']
        self.assertEqual(this_test, this_expected_results, 'results match')
        
    def test_update_rules(self):
        r = Rules()
        rules = r.get_rules()
        
        rules[RHEL]['memtotal'] = [0, 9388608, '< 9GB', 9388608, -1, '> 9GB' ]
        r.update_rules(rules)
        
        new_rules = r.get_rules()
        this_test = new_rules[RHEL]['memtotal']
        this_expected_results = [0, 9388608, '< 9GB', 9388608, -1, '> 9GB' ]
        self.assertEqual(this_test, this_expected_results, 'results match')
    