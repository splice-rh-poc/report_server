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

