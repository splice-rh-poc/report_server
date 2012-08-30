from django.db import models
from mongoengine import DateTimeField, Document, EmbeddedDocument,\
 EmbeddedDocumentField, ListField, ReferenceField, StringField, DictField
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
    
    def __unicode__(self):
        return u'%s %s' % (self.description, self.hostname)

class SpliceServerRelationships(Document):
    self = ReferenceField(SpliceServer, required=True)
    parent = ReferenceField(SpliceServer)
    children = ListField(ReferenceField(SpliceServer))

class MarketingProduct(Document):
    uuid = StringField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField()
    
    def __unicode__(self):
        return u'%s %s %s' % (self.uuid, self.name, self.description)

class MarketingProductSubscription(EmbeddedDocument):
    expires = DateTimeField(required=True)
    product = ReferenceField(MarketingProduct, required=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.expires, self.product)

'''
class ConsumerIdentity(Document):
    uuid = StringField(required=True, unique=True)  # matches the identifier from the identity certificate
    subscriptions = ListField(EmbeddedDocumentField(MarketingProductSubscription))
    
    #def __unicode__(self):
    #    return u'%s' % (self.uuid)
    def __unicode__(self):
        return '%s' % (self.uuid)
'''
     
class ConsumerIdentity(Document):
    uuid = StringField(required=True, unique=True)  # matches the identifier from the identity certificate
    products = ListField(StringField())

    def __str__(self):
        return  '%s' % (self.uuid)

class ReportingItem(EmbeddedDocument):
    product = ReferenceField(MarketingProduct, required=True)
    date = DateTimeField(required=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.product, self.date)

'''
class ProductUsage(Document):
    consumer = ReferenceField(ConsumerIdentity)
    splice_server = ReferenceField(SpliceServer, required=True)
    instance_identifier = StringField(required=True, unique_with=["splice_server", "consumer"]) # example: MAC Address
    product_info = ListField(EmbeddedDocumentField(ReportingItem))
    
    def __unicode__(self):
        return u'%s %s %s %s' % (self.consumer, self.splice_server.hostname,
                                  self.instance_identifier, self.product_info)
'''
class ProductUsage(Document):
    consumer = ReferenceField(ConsumerIdentity)
    splice_server = ReferenceField(SpliceServer, required=True)
    instance_identifier = StringField(required=True) # example: MAC Address
    product_info = ListField(StringField())
    facts = DictField()
    date = DateTimeField(required=True)

    def __str__(self):
        return "Consumer '%s' on Splice Server '%s' from instance '%s' using products '%s' at '%s'" % \
               (self.consumer, self.splice_server, self.instance_identifier, self.product_info, self.date)


class ProductUsageForm(DocumentForm):
    #works
    class Meta:
        document = ProductUsage
        #consumer = document.consumer.choices
        #fields = ['splice_server', 'consumer']
        fields = ['consumer', 'splice_server']
    #works
        #consumers = forms.ModelChoiceField(queryset=ConsumerIdentity.objects.all())
        #fields = ['splice_server']
    #uuid = forms.ChoiceField(initial=ConsumerIdentity.objects.all())
        
class ConsumerIdentityForm(DocumentForm):
    class Meta:
        document = ConsumerIdentity
        #fields = ['uuid']




        
        