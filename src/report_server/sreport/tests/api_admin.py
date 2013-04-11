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

from report_server.sreport.models import ReportData, MarketingReportData, QuarantinedReportData, Pool, Product, Rules
from report_server.sreport.tests.general import BaseMongoTestCase, MongoApiTestCase
from rhic_serve.common.tests import BaseMongoTestCase#, MongoApiTestCase
from setup import TestData
from datetime import datetime, timedelta
import json

from splice.common import utils

class ImportAPITest(MongoApiTestCase):
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

    def test_post_duplicate(self):
        entry = TestData.create_product_usage_json()
        resp0 = self.api_client.post(
            '/api/v1/productusage/', format='json', data=entry)
        resp1 = self.api_client.post(
            '/api/v1/productusage/', format='json', data=entry)
        self.assertEqual(
            202, resp0.status_code, 'http status code is expected')
        #duplicates are now only logged and not rejected w/ a 409
        self.assertEqual(
            202, resp1.status_code, 'http status code is expected')

        self.assertEqual(1, ReportData.objects.all().count(),
                         'product_usuage successfully imported')
        #get a 202, but still there is only one object in db
        self.assertEqual(1, ReportData.objects.all().count(),
                         'product_usuage successfully imported')

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
        

class MarketingProductUsageAPITest(MongoApiTestCase):
    def setUp(self):
        super(MarketingProductUsageAPITest, self).setUp()
        self.drop_collections()

    def drop_collections(self):
        MarketingReportData.drop_collection()
        QuarantinedReportData.drop_collection()

    # Below is not running until we update the API to use the X509 cert for auth
    def UPDATE_LATER_test_with_no_authentication(self):
        resp = self.api_client.post(
            '/api/v1/marketingproductusage/', data="dummy data")
        self.assertEqual(401, resp.status_code, 'unauthorized is expected')

    def test_post_204(self):
        self.assertEqual(0, MarketingReportData.objects.all().count())    
        pool = TestData.create_candlepin_pool()
        product = TestData.create_candlepin_product()    
        mpu_entry_json = TestData.create_marketing_product_usage_json()
        resp = self.api_client.post(
            '/api/v1/marketingproductusage/', data=mpu_entry_json,
            SSL_CLIENT_CERT=self.valid_identity_cert_pem)
        self.assertEqual(204, resp.status_code, 'http status code is expected')

        self.assertEqual(2, MarketingReportData.objects.all().count(),
                         'marketing product_usuage successfully imported')
        self.assertEqual(0, QuarantinedReportData.objects.all().count(),
                         'asserted no marketing product usuage quarantined')

class PoolAPITest(MongoApiTestCase):
    def setUp(self):
        super(PoolAPITest, self).setUp()
        self.drop_collections()

    def drop_collections(self):
        Pool.drop_collection()

    def test_post_204(self):
        self.assertEqual(0, Pool.objects.all().count())    
        pool_entry_json = TestData.create_candlepin_pool_json()
        resp = self.api_client.post(
            '/api/v1/pool/', data=pool_entry_json,
            SSL_CLIENT_CERT=self.valid_identity_cert_pem)
        self.assertEqual(204, resp.status_code, 'http status code is expected')
        self.assertEqual(1, Pool.objects.all().count())


class ProductAPITest(MongoApiTestCase):
    def setUp(self):
        super(ProductAPITest, self).setUp()
        self.drop_collections()

    def drop_collections(self):
        Product.drop_collection()

    def test_post_204(self):
        self.assertEqual(0, Product.objects.all().count())    
        product_entry_json = TestData.create_candlepin_product_json()
        resp = self.api_client.post(
            '/api/v1/product/', data=product_entry_json,
            SSL_CLIENT_CERT=self.valid_identity_cert_pem)
        self.assertEqual(204, resp.status_code, 'http status code is expected')
        self.assertEqual(1, Product.objects.all().count())


class RulesAPITest(MongoApiTestCase):
    def setUp(self):
        super(RulesAPITest, self).setUp()
        self.drop_collections()

    def drop_collections(self):
        Rules.drop_collection()

    def test_post_204(self):
        self.assertEqual(0, Rules.objects.all().count())    
        rules_entry_json = TestData.create_candlepin_rules_json()
        resp = self.api_client.post(
            '/api/v1/rules/', data=rules_entry_json,
            SSL_CLIENT_CERT=self.valid_identity_cert_pem)
        self.assertEqual(204, resp.status_code, 'http status code is expected')
        self.assertEqual(1, Rules.objects.all().count())

class SpliceServerAPITest(MongoApiTestCase):
    def setUp(self):
        super(SpliceServerAPITest, self).setUp()
        self.drop_collections()

    def drop_collections(self):
        SpliceServer.drop_collection()

    def test_post_204(self):
        self.assertEqual(0, SpliceServer.objects.all().count())    
        spliceserver_entry_json = TestData.create_splice_server()
        resp = self.api_client.post(
            '/report-server/api/v1/spliceserver/', data=spliceserver_entry_json,
            SSL_CLIENT_CERT=self.valid_identity_cert_pem)
        self.assertEqual(204, resp.status_code, 'http status code is expected')
        self.assertEqual(1, SpliceServer.objects.all().count())


class QuarantinedDataTest(BaseMongoTestCase):
    def setUp(self):
        super(QuarantinedDataTest, self).setUp()
        self.drop_collections()

    def drop_collections(self):
        ReportData.drop_collection()
        QuarantinedReportData.drop_collection()

    def test_getlist(self):
        #create json here
        n = (datetime.now() + timedelta(days=1)).strftime('%s')
        entry = TestData.create_product_usage_json()
        #entry["date"] = "abcd"
        
        """
        Its unclear what would cause a pu object to be thrown into quarantine.
        Disabling this test for now
        
        resp0 = self.api_client.post('/api/v1/productusage/', 
                                     format='json',
                                     data=entry)
        self.assertEqual(200, resp0.status_code, 'http status code is expected')
        self.assertEqual(QuarantinedReportData.objects.count(), 1)
        
        resp1 = self.api_client.post('/api/v1/productusage/',
                                     format='json',
                                     data=entry)
        self.assertEqual(409, resp1.status_code, 'http status code is expected')
        self.assertEqual(ReportData.objects.count(), 1)
        self.assertEqual(QuarantinedReportData.objects.count(), 1)
        
        resp = self.api_client.get('/api/v1/quarantineddata/', format='json')
        self.assertContains(resp, '"instance_identifier": "00:11"',
                            count=1, status_code=200)
        """

class ComplianceDataTest(MongoApiTestCase):
    def setUp(self):
        super(ComplianceDataTest, self).setUp()
        self.drop_collections()

    def drop_collections(self):
        ReportData.drop_collection()
       

    def test_getlist(self):
        #create json here, memory greater than biz rules allow
        e = TestData.create_product_usage_json(memory='604836000000')
        entry = json.dumps(e)
        
        resp = self.post('/api/v1/productusage/', 
                                     data=entry
                                     )
        self.assertEqual(202, resp.status_code, 'http status code is expected')
        self.assertEqual(ReportData.objects.count(), 1)
  
        resp = self.get('/api/v1/compliancedata/')

        self.assertEqual(200, resp.status_code, 'http status code is expected')
        self.assertContains(resp, '"rule": "0 > 8388608; 8388608 > 83886080"',
                                    count=1, status_code=200) 
