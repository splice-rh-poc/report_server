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

from mongoengine import DateTimeField, Document, EmbeddedDocument, EmbeddedDocumentField, \
  ListField, ReferenceField, StringField, DictField, UUIDField, FileField, IntField
from django import forms
from splice.entitlement.models import ProductUsage, SpliceServer, SpliceServerRelationships, ConsumerIdentity
from mongodbforms import DocumentForm, EmbeddedDocumentForm
from mongoengine.queryset import QuerySet
from rhic_serve.rhic_rcs.models import RHIC



class ProductUsageForm(DocumentForm):
    #works
    class Meta:
        document = ProductUsage
        #consumer = document.consumer.choicesI
        fields = ['splice_server', 'consumer']
        #fields = ['consumer', 'splice_server']
    #works
        #consumers = forms.ModelChoiceField(queryset=ConsumerIdentity.objects.all())
        #fields = ['splice_server']
    #uuid = forms.ChoiceField(initial=ConsumerIdentity.objects.all())

    # choices is a list of tuples in the form ("value", "label")
    # We are asking mongo to give us the distinct consumer uuids used by ProductUsage
    consumer_choices = [(rhic_id, rhic_id ) for rhic_id in ProductUsage.objects().distinct("consumer")]
    consumer = forms.ChoiceField(required=True, choices=consumer_choices)
    splice_server_choices = [(server_id, server_id) for server_id in ProductUsage.objects().distinct("splice_server")]
    splice_server = forms.ChoiceField(choices=splice_server_choices)
        
    meta = {'db_alias': 'checkin'}



class ReportData(Document):
    instance_identifier = StringField(required=True)
    consumer = StringField(required=True)
    product = StringField(required=True)
    product_name =  StringField(required=True)
    date = DateTimeField(required=True)
    sla = StringField(required=True)
    support = StringField(required=True)
    contract_id = StringField(required=True)
    contract_use = StringField(required=True)
    hour = StringField(required=True)
    memtotal = IntField(required=True)
    cpu_sockets = IntField(required=True)
    environment = StringField(required=True)
    
    
    meta = {'db_alias': 'results'}
    
    
    






