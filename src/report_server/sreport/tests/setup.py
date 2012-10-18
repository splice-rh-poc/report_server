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
from sreport.models import ReportData, ReportDataDaily, MyQuerySet
from sreport.models import ProductUsage, SpliceServer
from rhic_serve.rhic_rest.models import RHIC, Account
from mongoengine.queryset import QuerySet
from mongoengine import Document, StringField, ListField, DateTimeField, IntField
from datetime import datetime, timedelta
from common.products import Product_Def
from common.utils import datespan
from common.report import get_list_of_products, hours_per_consumer
from common.import_util import import_data
from common import config
import collections
from dev.custom_count import Rules
from common import constants


LOG = getLogger(__name__)
config.init()
this_config = config.get_import_info()
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
    




            
RHEL = "RHEL Server"
HA = "RHEL HA"
EUS = "RHEL EUS"
LB = "RHEL LB"
JBoss = "JBoss EAP"
EDU = "RHEL Server for Education"
UNLIMITED = "RHEL Server 2-socket Unlimited Guest"
GEAR = "OpenShift Gear"

PRODUCTS_DICT={
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
    RHEL = "RHEL Server"
    HA = "RHEL HA"
    EUS = "RHEL EUS"
    LB = "RHEL LB"
    JBoss = "JBoss EAP"
    EDU = "RHEL Server for Education"
    UNLIMITED = "RHEL Server 2-socket Unlimited Guest"
    GEAR = "OpenShift Gear"

    PRODUCTS_DICT={
                     RHEL: (["69"], '8d401b5e-2fa5-4cb6-be64-5f57386fda86', "rhel-server-1190457-3116649-prem-l1-l3"), 
                     HA: (["83"], 'fbbd06c6-ebed-4892-87a3-2bf17c864444', 'rhel-ha-1190457-3874444-na-standard'),
                     EUS: (["70"],'fbbd06c6-ebed-4892-87a3-2bf17c865555', 'rhel-eus-1190457-3874444-prem-l1-l3'),
                     LB: (["85"], 'fbbd06c6-ebed-4892-87a3-2bf17c866666', 'rhel-lb-1190457-3874444-prem-l1-l3'),
                     JBoss: (["183"],'ee5c9aaa-a40c-1111-80a6-ef731076bbe8', 'jboss-1111730-4582732-prem-l1-l3'),
                     EDU: (["69"], 'fbbd06c6-ebed-4892-87a3-2bf17c86e610', 'rhel-server-education-1190457-3879847-na-ss'),
                     UNLIMITED: (["69"], 'fbbd06c6-ebed-4892-87a3-2bf17c867777', 'rhel-2socket_unlimited-1190457-3874444-prem-l1-l3'),
                     GEAR: (["69", "183"], 'b0e7bd8a-0b23-4b35-86d7-52a87311a5c2', 'openshift-gear-3485301-4582732-prem-l1-l3')
                    }

    @staticmethod
    def create_entry(product, mem_high=True, date=None, socket=4, cpu=4):
        rules = Rules()
        report_biz_rules = rules.get_rules()
        if not date:
            date = datetime.now()
        this_hour = date.strftime(constants.hr_fmt)
        this_day = date.strftime(constants.day_fmt)
        
        interval = report_biz_rules[product]['calculation']
        
        if interval == 'hourly':
            row = ReportData(
                                    instance_identifier = "12:31:3D:08:49:00",
                                    date =  date,
                                    hour = this_hour,
                                    environment = "us-east-1",
                                    splice_server = "splice-server-1.spliceproject.org"
                                    )
        elif interval == 'daily':
            row = ReportDataDaily(
                                    instance_identifier = "12:31:3D:08:49:00",
                                    date =  date,
                                    day = this_day,
                                    environment = "us-east-1",
                                    splice_server = "splice-server-1.spliceproject.org"
                                    )
        
        for key, value in PRODUCTS_DICT.items():
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
            
        
        for key, value in PRODUCTS_DICT.items():
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
    def create_product_usage(splice_server, facts, cdate, consumer='consumer01', instance='ident01', products=['69'], save=True):
        pu = ProductUsage(
             consumer=consumer,
             splice_server=splice_server,
             instance_identifier=instance,
             allowed_product_info=products,
             facts=facts,
             date=cdate
             )
        if save:
            pu.save(cascade=True)
        return pu

