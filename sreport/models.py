from django.db import models
from mongoengine import DateTimeField, Document, EmbeddedDocument,\
 EmbeddedDocumentField, ListField, ReferenceField, StringField
from django.db import models
from django import forms
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from mongodbforms import EmbeddedDocumentForm
from mongodbforms import DocumentForm
from mongodbforms.fieldgenerator import MongoFormFieldGenerator
from django.forms.models import ModelChoiceField
from django.forms.models import modelformset_factory

class SpliceServer(Document):
    uuid = StringField(required=True, unique=True)
    description = StringField() # Example what datacenter is this deployed to, i.e. us-east-1
    hostname = StringField(required=True)

class SpliceServerRelationships(Document):
    self = ReferenceField(SpliceServer, required=True)
    parent = ReferenceField(SpliceServer)
    children = ListField(ReferenceField(SpliceServer))

class MarketingProduct(Document):
    uuid = StringField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField()

class MarketingProductSubscription(EmbeddedDocument):
    expires = DateTimeField(required=True)
    product = ReferenceField(MarketingProduct, required=True)

class ConsumerIdentity(Document):
    uuid = StringField(required=True, unique=True)  # matches the identifier from the identity certificate
    subscriptions = ListField(EmbeddedDocumentField(MarketingProductSubscription))

class ReportingItem(EmbeddedDocument):
    product = ReferenceField(MarketingProduct, required=True)
    date = DateTimeField(required=True)

class ProductUsage(Document):
    consumer = ReferenceField(ConsumerIdentity)
    splice_server = ReferenceField(SpliceServer, required=True)
    instance_identifier = StringField(required=True, unique_with=["splice_server", "consumer"]) # example: MAC Address
    product_info = ListField(EmbeddedDocumentField(ReportingItem))


class ProductUsageForm(DocumentForm):
    class Meta:
        document = ProductUsage
        #consumers = forms.ModelChoiceField(queryset=ConsumerIdentity.objects.all())
        #fields = ['splice_server']
        
class ConsumerIdentityForm(DocumentForm):
    class Meta:
        document = ConsumerIdentity
        #fields = ['uuid']




        
        