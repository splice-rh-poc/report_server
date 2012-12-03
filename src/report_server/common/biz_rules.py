import json
import os
import collections
import logging


_LOG = logging.getLogger(__name__)

RHEL = "RHEL Server"
HA = "RHEL HA"
EUS = "RHEL EUS"
LB = "RHEL LB"
JBoss = "JBoss EAP"
EDU = "RHEL Server for Education"
UNLIMITED = "RHEL Server 2-socket Unlimited Guest"
GEAR = "OpenShift Gear"


'''
The dictionaries in this module should be replaced by an api call
to the mothership

Report Server Business Rules:
The report server database has rows of data with checkins of engineering
products, along w/ rhic data. It is up to the report server to translate that
raw data and engineering products into marketing products.
This translation is done with the following set of rules as they relate
to each systems facts.

This is a sample tool to create a python collection and save it in json format
which will be read by the report server at launch.

FORMAT:
dict[PRODUCT NAME][query parameter] = Value tuple

Value Tuple Format : six entries
1. = RANGE LOW Greater Than
2. = RANGE LOW Less Than
3. = RANGE LOW str(fact) as displayed in app
4. = RANGE HIGH Greater Than
5. = RANGE HIGH Less Than (-1 = no limit or not added to query)
6. = RANGE HIGH str(fact) as displayed in app

'''
report_biz_rules = collections.defaultdict(dict)
curr_dir = os.path.dirname(os.path.abspath(__file__))


path = '/tmp/report.json'


REPORT_RULES = None


class Rules:
    def init(self):
        global REPORT_RULES
        if REPORT_RULES:
            return REPORT_RULES

        interval = 'hourly'
        # interval = 'daily'

        '''
        This section will be replaced by some sort of api call to hosted to get
        the latest business rules.  The rules will then be written in json 
        to /etc/splice/report.py and obfuscated and a md5sum created 
        to prevent users from changing the business rules.. 
        '''
        # report_biz_rules['RHEL'] = RHEL
        report_biz_rules[RHEL]['cpu'] = []
        # report_biz_rules[RHEL]['memtotal']=[0, 8388608, '< 8GB', 8388608, -1,
        # '> 8GB']
        report_biz_rules[RHEL]['memtotal'] = {
            'low_gt': 0, 
            'low_lt': 8388608,
            'low_desc': '< 8GB',
            'high_gt': 8388608,
            'high_lt': 83886080,
            'high_desc': '> 8GB', 
            'rule': '0 > 8388608; 8388608 > 83886080'
        }
        report_biz_rules[RHEL]['cpu_sockets'] = []
        report_biz_rules[RHEL]['calculation'] = interval

        report_biz_rules[JBoss]['cpu'] = []
        report_biz_rules[JBoss]['memtotal'] = []
        report_biz_rules[JBoss]['cpu_sockets'] = {
            'low_gt': 0, 
            'low_lt': 5, 
            'low_desc': '<= 4 Sockets',
            'high_gt': 4, 
            'high_lt': 6,
            'high_desc': '> 4 Sockets',
            'rule': '<= 4 ; 4 > 6'
        }
        report_biz_rules[JBoss]['calculation'] = interval

        report_biz_rules[GEAR]['cpu'] = {
            'low_gt': 0,
            'low_lt': 2,
            'low_desc': ' 1 cpu',
            'high_gt': 1,
            'high_lt': 5,
            'high_desc': '> 1 cpu',
            'rule': '0 > 2; > 1'
        }
        report_biz_rules[GEAR]['memtotal'] = {
            'low_gt': 0,
            'low_lt': 2097153,
            'low_desc': ' <= 2GB',
            'high_gt': 2097152,
            'high_lt': -1,
            'high_desc': '> 2GB',
            'rule': '0 > 2097153;  2097152 > -1'
        }
        report_biz_rules[GEAR]['cpu_sockets'] = []
        report_biz_rules[GEAR]['calculation'] = interval

        report_biz_rules[UNLIMITED]['cpu'] = []
        report_biz_rules[UNLIMITED]['memtotal'] = []
        report_biz_rules[UNLIMITED]['cpu_sockets'] = {
            'low_gt': 0,
            'low_lt': 3,
            'low_desc': ' <= 2 CPU Sockets',
            'high_gt': 2,
            'high_lt': 5,
            'high_desc': '2 > socket <= 4 ',
            'rule': '0 > 3; 2 > 5'}
        report_biz_rules[UNLIMITED]['calculation'] = interval

        report_biz_rules[HA]['cpu'] = []
        report_biz_rules[HA]['memtotal'] = {
            'low_gt': 0,
            'low_lt': 8388608,
            'low_desc': '< 8GB',
            'high_gt': 8388608,
            'high_lt': 83886080,
            'high_desc': '> 8GB',
            'rule': '0 > 8388608; 8388608 > 83886080'
        }
        report_biz_rules[HA]['cpu_sockets'] = []
        report_biz_rules[HA]['calculation'] = ['hourly']
        report_biz_rules[HA]['calculation'] = interval

        report_biz_rules[EUS]['cpu'] = []
        report_biz_rules[EUS]['memtotal'] = {
            'low_gt': 0,
            'low_lt': 8388608,
            'low_desc': '< 8GB',
            'high_gt': 8388608,
            'high_lt': 83886080,
            'high_desc': '> 8GB',
            'rule': '0 > 8388608; 8388608 > 83886080'
        }
        report_biz_rules[EUS]['cpu_sockets'] = []
        report_biz_rules[EUS]['calculation'] = ['daily']
        report_biz_rules[EUS]['calculation'] = interval

        report_biz_rules[EDU]['cpu'] = []
        report_biz_rules[EDU]['memtotal'] = {
            'low_gt': 0,
            'low_lt': 8388608,
            'low_desc': '< 8GB',
            'high_gt': 8388608,
            'high_lt': -1,
            'high_desc': '> 8GB',
            'rule': '0 > 8388608; > 8388608'
        }
        report_biz_rules[EDU]['cpu_sockets'] = []
        report_biz_rules[EDU]['calculation'] = interval

        report_biz_rules[LB]['cpu'] = []
        report_biz_rules[LB]['memtotal'] = {
            'low_gt': 0,
            'low_lt': 8388608,
            'low_desc': '< 8GB',
            'high_gt': 8388608,
            'high_lt': 83886080,
            'high_desc': '> 8GB',
            'rule': '0 > 8388608; 8388608 > 83886080'
        }
        report_biz_rules[LB]['cpu_sockets'] = []
        report_biz_rules[LB]['calculation'] = interval

        with open(path, 'wb') as rulz:
            json.dump(report_biz_rules, rulz)
            print('rule written')
        with open(path, 'rb') as final_rules:
            REPORT_RULES = json.load(final_rules)

    def list_rules(self):
        with open(path, 'rb') as rulz:
            report_rules = json.load(rulz)
        print(report_rules)
        _LOG.info('report server rules=' + str(report_rules))

    def get_rules(self):
        return REPORT_RULES

    def update_rules(self, new_rules):
        REPORT_RULES = new_rules
