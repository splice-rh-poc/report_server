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

from report_server.sreport.models import ReportData, QuarantinedReportData
from report_server.sreport.tests.general import BaseReportTestCase
from setup import TestData


class ImportAPITest(BaseReportTestCase):
    def setUp(self):
        super(ImportAPITest, self).setUp()
        self.drop_collections()
        self.detail_url = '/api/v1/productusage/'

    def drop_collections(self):
        ReportData.drop_collection()
        QuarantinedReportData.drop_collection()

    def test_post_202(self):
        self.assertEqual(0, ReportData.objects.all().count(),
                                 'product_usuage successfully imported')        
        entry = TestData.create_product_usage_json()
        resp = self.api_client.post(
            '/api/v1/productusage/', format='json', data=entry)
        self.assertEqual(202, resp.status_code, 'http status code is expected')

        self.assertEqual(1, ReportData.objects.all().count(),
                         'product_usuage successfully imported')
        self.assertEqual(0, QuarantinedReportData.objects.all().count(),
                         'asserted no product usuage quarantined')

    def test_post_409(self):
        entry = TestData.create_product_usage_json()
        resp0 = self.api_client.post(
            '/api/v1/productusage/', format='json', data=entry)
        resp1 = self.api_client.post(
            '/api/v1/productusage/', format='json', data=entry)
        self.assertEqual(
            202, resp0.status_code, 'http status code is expected')
        self.assertEqual(
            409, resp1.status_code, 'http status code is expected')

        self.assertEqual(1, ReportData.objects.all().count(),
                         'product_usuage successfully imported')
        self.assertEqual(1, QuarantinedReportData.objects.all().count(),
                         'asserted 1 product usuage quarantined')

    def test_post_unique_ident(self):
        entry1 = TestData.create_product_usage_json(instance_identifier='00:11')
        entry2 = TestData.create_product_usage_json(instance_identifier='00:22')
        
        resp0 = self.api_client.post('/api/v1/productusage/', 
                                     format='json', 
                                     data=entry1)
        resp1 = self.api_client.post('/api/v1/productusage/',
                                     format='json', 
                                     data=entry2)
        
        self.assertEqual(202, resp0.status_code, 'http status code is expected')
        self.assertEqual(202, resp1.status_code, 'http status code is expected')

        self.assertEqual(2, ReportData.objects.all().count(),
                         'product_usuage successfully imported')
        self.assertEqual(0, QuarantinedReportData.objects.all().count(),
                         'asserted 1 product usuage quarantined')
        
        
        


class QuarantinedDataTest(BaseReportTestCase):
    def setUp(self):
        super(QuarantinedDataTest, self).setUp()
        self.drop_collections()

    def drop_collections(self):
        ReportData.drop_collection()
        QuarantinedReportData.drop_collection()

    def test_getlist(self):
        #create json here
        entry = TestData.create_product_usage_json()
        resp0 = self.api_client.post('/api/v1/productusage/', 
                                     format='json',
                                     data=entry)
        self.assertEqual(202, resp0.status_code, 'http status code is expected')
        self.assertEqual(ReportData.objects.count(), 1)
        
        resp1 = self.api_client.post('/api/v1/productusage/',
                                     format='json',
                                     data=entry)
        self.assertEqual(409, resp1.status_code, 'http status code is expected')
        self.assertEqual(ReportData.objects.count(), 1)
        self.assertEqual(QuarantinedReportData.objects.count(), 1)
        
        resp = self.api_client.get('/api/v1/quarantineddata/', format='json')
        self.assertContains(resp, '"instance_identifier": "00:11"',
                            count=1, status_code=200)

class ComplianceDataTest(BaseReportTestCase):
    def setUp(self):
        super(ComplianceDataTest, self).setUp()
        self.drop_collections()

    def drop_collections(self):
        ReportData.drop_collection()
       

    def test_getlist(self):
        #create json here, memory greater than biz rules allow
        entry = TestData.create_product_usage_json(memory='604836000000')
        resp = self.api_client.post('/api/v1/productusage/', 
                                     format='json',
                                     data=entry)
        self.assertEqual(202, resp.status_code, 'http status code is expected')
        self.assertEqual(ReportData.objects.count(), 1)
        

        resp = self.api_client.get('/api/v1/compliancedata/', format='json')
        self.assertEqual(200, resp.status_code, 'http status code is expected')
        self.assertContains(resp, '"rule": "0 > 8388608; 8388608 > 83886080"',
                                    count=1, status_code=200) 
        

        
            
        
        
