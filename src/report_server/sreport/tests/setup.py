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

import collections
from datetime import datetime, timedelta
from django.test import TestCase
from django.conf import settings
from logging import getLogger
from mongoengine.connection import connect, disconnect
from mongoengine import connection, register_connection
from mongoengine.queryset import QuerySet
from mongoengine import Document, StringField, ListField, DateTimeField,\
    IntField
from report_server.common.biz_rules import Rules
from report_server.common import constants
from report_server.common.products import Product_Def
from report_server.common.utils import datespan
from report_server.common.report import get_list_of_products, hours_per_consumer
from report_server.common.import_util import import_data
from report_server.common import config
from report_server.sreport.models import ReportData, ReportDataDaily, MyQuerySet
from report_server.sreport.models import ProductUsage, SpliceServer
from rhic_serve.rhic_rest.models import RHIC, Account
from rhic_serve.common.tests import BaseMongoTestCase, MongoApiTestCase
#from splice.common.models import ProductUsage


LOG = getLogger(__name__)
# this_config = config.get_import_info()


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

class ReportData(ReportData):
    db_name = settings.MONGO_DATABASE_NAME
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
    support_level = StringField(
        required=True, choices=support_level_choices.keys())
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

PRODUCTS_DICT = {
    # RHEL and JBOSS are now using the same RHIC
    RHEL: (["69"], 'fea363f5-af37-4a23-a2fd-bea8d1fff9e8',
           "rhel-server-jboss-1190457-3116649-prem-l1-l3"),

    HA: (["83"], 'fbbd06c6-ebed-4892-87a3-2bf17c864444',
         'rhel-ha-1190457-3874444-na-standard'),

    EUS: (["70"], 'fbbd06c6-ebed-4892-87a3-2bf17c865555',
          'rhel-eus-1190457-3874444-prem-l1-l3'),

    LB: (["85"], 'fbbd06c6-ebed-4892-87a3-2bf17c866666',
         'rhel-lb-1190457-3874444-prem-l1-l3'),

    JBoss: (["183"], 'fea363f5-af37-4a23-a2fd-bea8d1fff9e8',
            "rhel-server-jboss-1190457-3116649-prem-l1-l3"),

    EDU: (["69"], 'fbbd06c6-ebed-4892-87a3-2bf17c86e610',
          'rhel-server-education-1190457-3879847-na-ss'),

    UNLIMITED: (["69"], 'fbbd06c6-ebed-4892-87a3-2bf17c867777',
                'rhel-2socket_unlimited-1190457-3874444-prem-l1-l3'),

    GEAR: (["69", "183"], 'b0e7bd8a-0b23-4b35-86d7-52a87311a5c2',
           'openshift-gear-3485301-4582732-prem-l1-l3')
}


class TestData():

    RHEL = RHEL
    HA = HA
    EUS = EUS
    LB = LB
    JBoss = JBoss
    EDU = EDU
    UNLIMITED = UNLIMITED
    GEAR = GEAR

    PRODUCTS_DICT = PRODUCTS_DICT

    @staticmethod
    def create_entry(product,
                     mem_high=True,
                     date=None,
                     socket=4,
                     cpu=4,
                     instance_identifier="12:31:3D:08:49:00"):
        rules = Rules()
        report_biz_rules = rules.get_rules()
        if not date:
            date = datetime.now()
        this_hour = date.strftime(constants.hr_fmt)
        this_day = date.strftime(constants.day_fmt)

        interval = report_biz_rules[product]['calculation']

        if interval == 'hourly':
            row = ReportData(
                instance_identifier=instance_identifier,
                date=date,
                hour=this_hour,
                day=this_day,
                environment="us-east-1",
                splice_server="test01"
            )
        elif interval == 'daily':
            row = ReportDataDaily(
                instance_identifier=instance_identifier,
                date=date,
                day=this_day,
                environment="us-east-1",
                splice_server="test01"
            )

        for key, value in PRODUCTS_DICT.items():
            if product == key:
                rhic = RHIC.objects.filter(uuid=value[1])[0]
                row['product_name'] = key
                row['product'] = value[0]
                row['consumer_uuid'] = value[1]
                row['consumer'] = value[2]
                row['contract_id'] = rhic.contract
                row['sla'] = rhic.sla
                row['support'] = rhic.support_level
                row['contract_use'] = "20"
                row['cpu_sockets'] = socket
                row['cpu'] = cpu
                row['record_identifier'] = str(value[2]) + instance_identifier\
                    + str(date) + str(value[0])

        if mem_high:
            row['memtotal'] = 16048360
            return row
        else:
            row['memtotal'] = 640
            return row

    @staticmethod
    def create_products():
        # currently we rely on specific rhics to be created by the
        # generate_product_usage script in splice-server/playpen
        # assert that appears to be sane..

        num = RHIC.objects.all().count()
        if num != 9:
            raise Exception('rhics in rhic_serve db may not be valid')

        for key, value in PRODUCTS_DICT.items():
            # print('create_product', key)
            #print(RHIC.objects.count())
            #print(value[1])
            #all_rhics = RHIC.objects.all()
            rhic = RHIC.objects.filter(uuid=value[1])[0]
            contract_num = rhic.contract
            # print('contract_num', contract_num)
            # print('account_id', rhic.account_id)
            list_of_products = get_list_of_products(
                rhic.account_id, contract_num)

            products_contract = [(prod.name) for prod in list_of_products]
            intersect = set(products_contract).intersection(set(rhic.products))
            # print(intersect)
            if len(intersect) < 1:
                raise Exception('rhics and account/contracts in rhic_serve'
                                'db may not be valid')

            for p in list_of_products:
                # print p.name
                if p.name == key:
                    row = Product(
                        quantity=p.quantity,
                        support_level=p.support_level,
                        sla=p.sla,
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
                    'products': [RHEL, HA, EDU, EUS, LB, JBoss, GEAR],
                    'engineering_ids': ["69", "83", "70", "85", "183"]
        }

        RHIC.objects.get_or_create(rhic)

    @staticmethod
    def create_splice_server(hostname='splice01.example.com',
                             environment="east"):
        ss = SpliceServer(
            uuid=hostname,
            description=hostname,
            hostname=hostname,
            environment=environment
        )
        ss.save()
        return ss

    @staticmethod
    def create_product_usage(
        splice_server, facts, cdate, consumer='consumer01',
            instance='ident01', products=['69'], save=True):
        pu = ProductUsage(
            consumer=consumer,
            splice_server=splice_server.uuid,
            instance_identifier=instance,
            allowed_product_info=products,
            facts=facts,
            date=cdate
        )
        if save:
            pu.save(cascade=True)
        return pu
    
    @staticmethod
    def create_product_usage_json(
                                instance_identifier='00:11',
                                product_pem='69',
                                cpu='1',
                                socket='1',
                                memory='604836'
                                ):
        entry = {
            "_types": ["ProductUsage", "ProductUsage.ProductUsage"],
            "splice_server": "test01",
            "allowed_product_info": [product_pem],
            "unallowed_product_info": [],
            "date": {"$date": 1352424600000},
            "_cls": "ProductUsage.ProductUsage",
            "instance_identifier": instance_identifier,
            "facts": {"lscpu_dot_cpu(s)": cpu,
                      "memory_dot_memtotal": memory,
                      "lscpu_dot_cpu_socket(s)": socket},
            "consumer": "fea363f5-af37-4a23-a2fd-bea8d1fff9e8"
        }
        return entry
