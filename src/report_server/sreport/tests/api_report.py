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
from report_server.sreport.tests.general import BaseReportTestCase
from report_server.sreport.tests.general import BaseMongoApiTestCase
from setup import TestData

"""
class ReportDataTest(BaseMongoApiTestCase):
    def setUp(self):
        super(ReportDataTest, self).setUp()
        self.drop_collections()
        
        
    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)    
        

    def drop_collections(self):
        ReportData.drop_collection()
    
    def get_default_user(self):
        return Account.objects.get(login='shadowman@redhat.com')  

    def test_getlist(self):        
        
        #create json here, a valid entry
        entry = TestData.create_product_usage_json()
        resp = self.client.post('/api/v1/productusage/', 
                                     format='json',
                                     data=entry)
        self.assertEqual(202, resp.status_code, 'http status code is expected')
        
        query = {"user": "shadowman@redhat.com", "byMonth": "11,2012",\
                  "contract_number": "All", "rhic": "null", "env": "All"}
        
        resp = self.client.post('/api/v1/report/', 
                                    authentication=self.get_default_user(),
                                    data=query,
                                    format='json')
        self.assertEqual(200, resp.status_code, 'http status code is expected')
        self.assertContains(resp, '"instance_identifier": "00:11"',\
                            count=1, status_code=200) 
"""