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

import datetime
from django.contrib.auth.models import User
from report_server.sreport.models import ReportData, QuarantinedReportData
from report_server.sreport.tests.general import BaseReportTestCase


class ImportAPITest(BaseReportTestCase):
    
    def setUp(self):
        super(ImportAPITest, self).setUp()
        self.dropCollections()

        
        self.detail_url = '/api/v1/productusage/'
        
        
    def dropCollections(self):
        ReportData.drop_collection()
        QuarantinedReportData.drop_collection()
        
    
    def createJSON(self, instance_identifier='00:11',
                    product_pem = '69',
                    cpu = '1',
                    socket = '1',
                    memory = '604836'
                    ):
        entry = {          
                   "_types" : [ "ProductUsage", "ProductUsage.ProductUsage" ],
                   "splice_server" : "test01",
                   "allowed_product_info" : [ product_pem ], 
                   "unallowed_product_info" : [], 
                   "date" : { "$date" : 1352424600000 }, 
                   "_cls" : "ProductUsage.ProductUsage", 
                   "instance_identifier" : instance_identifier, 
                   "facts" : { "lscpu_dot_cpu(s)" : cpu, 
                              "memory_dot_memtotal" : memory, 
                              "lscpu_dot_cpu_socket(s)" : socket}, 
                   "consumer" : "fea363f5-af37-4a23-a2fd-bea8d1fff9e8" 
                   }
        return entry
        
    def test_post_202(self):
        resp = self.api_client.post('/api/v1/productusage/', format='json', data=self.createJSON())
        self.assertEqual(202, resp.status_code, 'http status code is expected')
        
        #print('number of items in report db:' + str(ReportData.objects.all().count()))
        #print('number of items in quarantine db:' + str(QuarantinedReportData.objects.all().count()))
        
        self.assertEqual(1, ReportData.objects.all().count(), 'product_usuage successfully imported' )
        self.assertEqual(0, QuarantinedReportData.objects.all().count(), 'asserted no product usuage quarantined' )
    
    def test_post_409(self):
        resp0 = self.api_client.post('/api/v1/productusage/', format='json', data=self.createJSON())
        resp1 = self.api_client.post('/api/v1/productusage/', format='json', data=self.createJSON())
        self.assertEqual(202, resp0.status_code, 'http status code is expected')
        self.assertEqual(409, resp1.status_code, 'http status code is expected')

        self.assertEqual(1, ReportData.objects.all().count(), 'product_usuage successfully imported' )
        self.assertEqual(1, QuarantinedReportData.objects.all().count(), 'asserted 1 product usuage quarantined' )

    def test_post_unique_ident(self):
        resp0 = self.api_client.post('/api/v1/productusage/', format='json', data=self.createJSON(instance_identifier='00:11'))
        resp1 = self.api_client.post('/api/v1/productusage/', format='json', data=self.createJSON(instance_identifier='00:22'))
        self.assertEqual(202, resp0.status_code, 'http status code is expected')
        self.assertEqual(202, resp1.status_code, 'http status code is expected')
        
        
        self.assertEqual(2, ReportData.objects.all().count(), 'product_usuage successfully imported' )
        self.assertEqual(0, QuarantinedReportData.objects.all().count(), 'asserted 1 product usuage quarantined' )




class InstanceComplianceTest(BaseReportTestCase):
    
    def setUp(self):
        super(InstanceComplianceTest, self).setUp()
        self.dropCollections()

        
        self.detail_url = '/api/v1/productusage/'
        
        
    def dropCollections(self):
        ReportData.drop_collection()
        QuarantinedReportData.drop_collection()
        
    
    def createJSON(self, instance_identifier='00:11',
                    product_pem = '69',
                    cpu = '1',
                    socket = '1',
                    memory = '604836'
                    ):
        entry = {          
                   "_types" : [ "ProductUsage", "ProductUsage.ProductUsage" ],
                   "splice_server" : "test01",
                   "allowed_product_info" : [ product_pem ], 
                   "unallowed_product_info" : [], 
                   "date" : { "$date" : 1352424600000 }, 
                   "_cls" : "ProductUsage.ProductUsage", 
                   "instance_identifier" : instance_identifier, 
                   "facts" : { "lscpu_dot_cpu(s)" : cpu, 
                              "memory_dot_memtotal" : memory, 
                              "lscpu_dot_cpu_socket(s)" : socket}, 
                   "consumer" : "fea363f5-af37-4a23-a2fd-bea8d1fff9e8" 
                   }
        return entry
        
    def test_getlist(self):
        resp = self.api_client.post('/api/v1/quarantine/', format='json')
        self.assertEqual(200, resp.status_code, 'http status code is expected')
        


