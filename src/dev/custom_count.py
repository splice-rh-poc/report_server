import json, os
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
Report Server Business Rules:
The report server database has rows of data with checkins of engineering products, along w/ rhic data
It is up to the report server to translate that raw data and engineering products into marketing products.
This translation is done with the following set of rules as they relate to each systems facts.

This is a sample tool to create a python collection and save it in json format which will be read by the report server at launch.

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
if 'report_server' in curr_dir:
    path = '../../etc/splice/report.json'
    print('PATH='+path)
else:
    path = '../etc/splice/report.json'
    print('PATH='+path)

REPORT_RULES = None

class Rules:
    def init(self): 
        global REPORT_RULES
        if REPORT_RULES:
            return REPORT_RULES
        
        interval = 'hourly'
        #interval = 'daily'

        '''
        This section will be replaced by some sort of api call to hosted to get the latest business rules
        The rules will then be written in json to /etc/splice/report.py and obfuscated and a md5sum created to prevent users
        from changing the business rules.. (or something like that)
        '''
        #report_biz_rules['RHEL'] = RHEL
        report_biz_rules[RHEL]['cpu']=[]
        report_biz_rules[RHEL]['memtotal']=[0, 8388608, '< 8GB', 8388608, -1, '> 8GB']
        report_biz_rules[RHEL]['cpu_sockets']=[]
        report_biz_rules[RHEL]['calculation']=interval
        
        
        report_biz_rules[JBoss]['cpu']=[]
        report_biz_rules[JBoss]['memtotal']= []
        report_biz_rules[JBoss]['cpu_sockets']=[0, 5, '<= 4 vCPU', 4, -1, '> 4 vCPU']
        report_biz_rules[JBoss]['calculation']=interval
        
        
        report_biz_rules[GEAR]['cpu']=[0, 2, ' 1 cpu', 1, -1, '> 1 cpu']
        report_biz_rules[GEAR]['memtotal']= [0, 2097153, ' <= 2GB', 2097152, -1, '> 2GB']
        report_biz_rules[GEAR]['cpu_sockets']=[]
        report_biz_rules[GEAR]['calculation']=interval
        
        report_biz_rules[UNLIMITED]['cpu']=[]
        report_biz_rules[UNLIMITED]['memtotal']=[]
        report_biz_rules[UNLIMITED]['cpu_sockets']=[0, 3, ' <= 2 CPU Sockets', 2, 5, '2 > socket <= 4 ']
        report_biz_rules[UNLIMITED]['calculation']=interval
        
        report_biz_rules[HA]['cpu']=[]
        report_biz_rules[HA]['memtotal']=[0, 8388608, '< 8GB', 8388608, -1, '> 8GB']
        report_biz_rules[HA]['cpu_sockets']=[]
        report_biz_rules[HA]['calculation']=['hourly']
        report_biz_rules[HA]['calculation']=interval
        
        report_biz_rules[EUS]['cpu']=[]
        report_biz_rules[EUS]['memtotal']=[0, 8388608, '< 8GB', 8388608, -1, '> 8GB']
        report_biz_rules[EUS]['cpu_sockets']=[]
        report_biz_rules[EUS]['calculation']=['daily']
        report_biz_rules[EUS]['calculation']=interval
        
        report_biz_rules[EDU]['cpu']=[]
        report_biz_rules[EDU]['memtotal']=[0, 8388608, '< 8GB', 8388608, -1, '> 8GB']
        report_biz_rules[EDU]['cpu_sockets']=[]
        report_biz_rules[EDU]['calculation']=interval
        
        report_biz_rules[LB]['cpu']=[]
        report_biz_rules[LB]['memtotal']=[0, 8388608, '< 8GB', 8388608, -1, '> 8GB']
        report_biz_rules[LB]['cpu_sockets']=[]
        report_biz_rules[LB]['calculation']=interval
        
        
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