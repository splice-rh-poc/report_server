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

from django import forms
from django.contrib.auth.models import User
from mongoengine import DateTimeField, Document, ListField, StringField, IntField
from mongodbforms import DocumentForm
from mongoengine.queryset import QuerySet
from splice.common.models import ProductUsage, SpliceServer, MarketingProductUsage


class MyQuerySet(QuerySet):

    def __init__(self, *args, **kwargs):
        super(MyQuerySet, self).__init__(*args, **kwargs)
        self._initial_query = {}
        self._document._collection = None
        self._collection_obj = self._document._get_collection()


class ProductUsage(ProductUsage):
    meta = {'db_alias': 'checkin_service',
            'queryset_class': MyQuerySet}
    
class MarketingProductUsage(MarketingProductUsage):
    meta = {'db_alias': 'checkin_service',
            'queryset_class': MyQuerySet}


class SpliceServer(SpliceServer):
    meta = {'db_alias': 'checkin_service',
            'queryset_class': MyQuerySet}

    def __str__(self):
        return "%s" % (self.environment)


class ProductUsageForm(DocumentForm):
    class Meta:
        document = ProductUsage
        # consumer = document.consumer.choicesI
        fields = ['splice_server', 'consumer']
        # fields = ['consumer', 'splice_server']
        # consumers = forms.ModelChoiceField(queryset=ConsumerIdentity.objects.all())
        # fields = ['splice_server']
        # uuid = forms.ChoiceField(initial=ConsumerIdentity.objects.all())

    # choices is a list of tuples in the form ("value", "label")
    # We are asking mongo to give us the distinct consumer uuids used by
    # ProductUsage
    consumer_choices = [(rhic_id, rhic_id) for rhic_id in ProductUsage.objects().distinct("consumer")]
    consumer = forms.ChoiceField(required=True, choices=consumer_choices)
    splice_server_choices = [(server_id, server_id) for server_id in ProductUsage.objects().distinct("splice_server")]
    splice_server = forms.ChoiceField(choices=splice_server_choices)

    meta = {'db_alias': 'checkin_service'}


class ReportData(Document):

    meta = {
        'db_alias': 'results',
        'allow_inheritance': True,
        'indexes': [('consumer_uuid', 'instance_identifier', 'hour',
                     'product'),
                    'date'],
    }

    instance_identifier = StringField(required=True)
    consumer_uuid = StringField(required=True)
    consumer = StringField(required=True)
    product = ListField(required=True)
    product_name = StringField(required=True)
    date = DateTimeField(required=True)
    sla = StringField(required=True)
    support = StringField(required=True)
    contract_id = StringField(required=True)
    contract_use = StringField(required=True)
    hour = StringField(required=True)
    day = StringField(required=True)
    memtotal = IntField(required=True)
    cpu_sockets = IntField(required=True)
    cpu = IntField(required=True)
    environment = StringField(required=True)
    splice_server = StringField(required=True)
    duplicate = IntField()
    record_identifier = StringField(required=True, unique_with=['consumer',
                                    'instance_identifier', 'hour', 'product'])

    def to_dict(self):
        return {'instance_identifier': self.instance_identifier,
                'consumer_uuid': self.consumer_uuid,
                'consumer': self.consumer,
                'product': self.product,
                'product_name': self.product_name,
                'date': self.date,
                'day': self.day,
                'sla': self.sla,
                'support': self.support,
                'contract_id': self.contract_id,
                'contract_use': self.contract_use,
                'hour': self.hour,
                'memtotal': self.memtotal,
                'cpu_sockets': self.cpu_sockets,
                'cpu': self.cpu,
                'environment': self.environment,
                'splice_server': self.splice_server,
                'duplicate': self.duplicate,
                'record_identifier': self.record_identifier
                }
    

class MarketingReportData(Document):

    meta = {
        'db_alias': 'results',
        'allow_inheritance': True,
        'indexes': [('splice_server', 'instance_identifier', 'hour',
                     'product'),
                    'date'],
    }

    instance_identifier = StringField(required=True)
    account = StringField(required=True)
    contract = StringField(required=True)
    product = StringField(required=True)
    product_name = StringField(required=True)
    quantity = IntField(required=True)
    date = DateTimeField(required=True)
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)
    hour = StringField(required=True)
    systemid = IntField(required=True)
    cpu_sockets = IntField(required=True)
    facts = StringField(required=True)
    environment = StringField(required=True)
    splice_server = StringField(required=True)
    record_identifier = StringField(required=True, unique_with=['splice_server',
                                    'instance_identifier', 'hour', 'product'])

    def to_dict(self):
        return {'instance_identifier': self.instance_identifier,
                'account': self.account,
                'contract': self.contract,
                'product': self.product,
                'product_name': self.product_name,
                'quantity': self.quantity,
                'date': self.date,
                'created': self.created,
                'updated': self.updated,
                'hour': self.hour,
                'systemid': self.systemid,
                'cpu_sockets': self.cpu_sockets,
                'facts': self.facts,
                'environment': self.environment,
                'splice_server': self.splice_server,
                'duplicate': self.duplicate,
                'record_identifier': self.record_identifier
                }


class ReportDataDaily(Document):

    meta = {
        'db_alias': 'results',
        'allow_inheritance': True,
        'indexes': [('consumer_uuid', 'instance_identifier', 'day',
                     'product'),
                    'date'],
    }

    instance_identifier = StringField(required=True)
    consumer_uuid = StringField(required=True)
    consumer = StringField(required=True)
    product = ListField(required=True)
    product_name = StringField(required=True)
    date = DateTimeField(required=True)
    sla = StringField(required=True)
    support = StringField(required=True)
    contract_id = StringField(required=True)
    contract_use = StringField(required=True)
    day = StringField(required=True)
    memtotal = IntField(required=True)
    cpu_sockets = IntField(required=True)
    cpu = IntField(required=True)
    environment = StringField(required=True)
    splice_server = StringField(required=True)
    duplicate = IntField()
    record_identifier = StringField(required=True, unique_with=['consumer',
                                    'instance_identifier', 'day', 'product'])


class ImportHistory(Document):
    meta = {
        'db_alias': 'results',
        'allow_inheritance': True,
        'indexes': [('date', 'splice_server')],
    }

    date = DateTimeField(required=True)
    splice_server = StringField(required=True)


class QuarantinedReportData(Document):
    meta = {
        'db_alias': 'results',
        'allow_inheritance': True,
        'indexes': [('consumer_uuid', 'instance_identifier', 'hour',
                     'product'),
                    'date'],
    }

    instance_identifier = StringField(required=True)
    consumer_uuid = StringField(required=True)
    consumer = StringField(required=True)
    product = ListField(required=True)
    product_name = StringField(required=True)
    date = DateTimeField(required=True)
    sla = StringField(required=True)
    support = StringField(required=True)
    contract_id = StringField(required=True)
    contract_use = StringField(required=True)
    hour = StringField(required=True)
    day = StringField(required=True)
    memtotal = IntField(required=True)
    cpu_sockets = IntField(required=True)
    cpu = IntField(required=True)
    environment = StringField(required=True)
    splice_server = StringField(required=True)
    duplicate = IntField()

      
class Account(Document):

    meta = {
        'db_alias': 'results'
    }

    # Unique account identifier
    account_id = StringField(unique=True, required=True)
    # Human readable account name
    login = StringField(unique=True, required=True)
    # List of contracts associated with the account.
    #contracts = ListField(EmbeddedDocumentField(Contract))


class SpliceUserProfile(User):
    meta = {
        'db_alias': 'results'
    }
    account = StringField(unique=True, required=True)


class SpliceAdminGroup(Document):
    meta = {
        'db_alias': 'results'
    }
    name = StringField(unique=True, required=True)
    members = ListField()
    permissions = ListField()

        


