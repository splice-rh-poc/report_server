"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from mongoengine import connect
from django.conf import settings
from tastypie.test import ResourceTestCase
from sreport.models import MarketingProduct


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class MongoTestCase(ResourceTestCase):
    """
    TestCase class that clear the collection between the tests
    """
    db_name = 'test_%s' % settings.MONGO_DATABASE_NAME
    def __init__(self, methodName='runtest'):
        self.db = connect(self.db_name)
        super(MongoTestCase, self).__init__(methodName)
    
    def test_data(self):
        self.assertTrue(MarketingProduct.objects)
        m = MarketingProduct.objects
        name = m[0].name.encode('utf-8')
        print(name)
        self.assertEqual(name, 'dummy_value_name_1', 'expected value matches')

    