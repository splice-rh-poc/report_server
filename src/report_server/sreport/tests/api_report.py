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

from django.contrib.auth.models import User
from report_server.sreport.models import ReportData
from rhic_serve.rhic_rest.models import Account
from report_server.sreport.tests.general import MongoApiTestCase
from setup import TestData
import json


class ReportDataTest(MongoApiTestCase):

    def setUp(self):
        super(ReportDataTest, self).setUp()
        self.drop_collections()
        self.detail_url = '/api/v1/report/'

    def drop_collections(self):
        ReportData.drop_collection()
    
    def test_getlist(self):        
        
        #create json here, a valid entry
        self.assertEqual(0, ReportData.objects.all().count())
        #print('count: ' + str(ReportData.objects.all().count()))
        e = TestData.create_product_usage_json(instance_identifier="00:11")
        entry = json.dumps(e)
        #print('ENTRY: ' + entry)
        resp = self.post('/api/v1/productusage/', 
                                     data=entry)
        #print('resp:' + str(resp.status_code))
        self.assertEqual(202, resp.status_code, 'http status code is expected')
        self.assertEqual(1, ReportData.objects.all().count())
        
        q = {"user": "shadowman@redhat.com", "byMonth": "11,2012", "contract_number": "All", "rhic": "null", "env": "All"}
        myquery = json.dumps(q)
        
        resp = self.post('/api/v1/reportmeter/', 
                        data=myquery,
                        code=200)
        #print(resp)
        self.assertEqual(200, resp.status_code, 'http status code is expected')
        self.assertContains(resp,
                            '"count": 1',
                            count=1, status_code=200) 
