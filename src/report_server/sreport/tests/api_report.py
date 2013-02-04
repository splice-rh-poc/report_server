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
from report_server.sreport.tests.general import MongoApiTestCase
from setup import TestData
import json


class ReportDataTest(MongoApiTestCase):
    """
    username="shadowman@redhat.com"
    password="shadowman@redhat.com"
    
    def setUp(self):
        super(ReportDataTest, self).setUp()
        self.drop_collections()
        
        
    def get_credentials(self):
        cred =  self.create_basic(username=self.username, password=self.password)
        return cred
        

    def drop_collections(self):
        ReportData.drop_collection()
    
    def get_default_user(self):
        return Account.objects.get(login='shadowman@redhat.com')  

    """
    def test_getlist(self):        
        
        #create json here, a valid entry
        e = TestData.create_product_usage_json(instance_identifier="00:11")
        entry = json.dumps(e)
        resp = self.post('/api/v1/productusage/', 
                                     data=entry)
        self.assertEqual(202, resp.status_code, 'http status code is expected')
        
        q = {"user": "shadowman@redhat.com", "byMonth": "11,2012",\
                  "contract_number": "All", "rhic": "null", "env": "All"}
        query = json.dumps(q)
        
        resp = self.post('/api/v1/report/', 
                                    data=query,
                                    code=200
                                    )
        self.assertEqual(200, resp.status_code, 'http status code is expected')
        self.assertContains(resp,
                            '"count": 1',
                            count=1, status_code=200) 
