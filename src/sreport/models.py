from mongoengine import DateTimeField, Document, EmbeddedDocument, EmbeddedDocumentField, \
  ListField, ReferenceField, StringField, DictField, UUIDField, FileField, IntField
from django import forms
from mongodbforms import DocumentForm, EmbeddedDocumentForm
from mongoengine.queryset import QuerySet




class SpliceServer(Document):
    uuid = StringField(required=True, unique=True)
    description = StringField() # Example what datacenter is this deployed to, i.e. us-east-1
    hostname = StringField(required=True)
    
    meta = {'db_alias': 'checkin'}
    
    def __unicode__(self):
        return u'%s %s' % (self.description, self.hostname)

class SpliceServerRelationships(Document):
    self = ReferenceField(SpliceServer, required=True)
    parent = ReferenceField(SpliceServer)
    children = ListField(ReferenceField(SpliceServer))
    
    meta = {'db_alias': 'checkin'}


class ConsumerIdentity(Document):
    uuid = StringField(required=True, unique=True)  # matches the identifier from the identity certificate
    products = ListField(StringField())
    
    meta = {'db_alias': 'checkin'}

    def __str__(self):
        return  '%s' % (self.uuid)

class ProductUsage(Document):
    consumer = StringField(required=True)
    splice_server = ReferenceField(SpliceServer, required=True)
    instance_identifier = StringField(required=True) # example: MAC Address
    product_info = ListField(StringField())
    facts = DictField()
    date = DateTimeField(required=True)
    
    meta = {'db_alias': 'checkin'}

    def __str__(self):
        return "Consumer '%s' on Splice Server '%s' from instance '%s' using products '%s' at '%s'" % \
               (self.consumer, self.splice_server, self.instance_identifier, self.product_info, self.date)

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

class ConsumerIdentityForm(DocumentForm):
    class Meta:
        document = ConsumerIdentity
        #fields = ['uuid']


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
    
    
    meta = {'db_alias': 'results'}
    
    
    
class BaseQuery(object):
    """
    BaseQuery and BaseQuerySet are 2 dummy classes to work around a mongoengine
    incompatibility with tastypie.  tastypie assumes each resources model
    queryset has a query object associated with it, and that query object has
    an attribute called query_terms.

    These classes work around that assumption.
    """
    query_terms = object()

class BaseQuerySet(QuerySet):
    """
    BaseQuery and BaseQuerySet are 2 dummy classes to work around a mongoengine
    incompatibility with tastypie.  tastypie assumes each resources model
    queryset has a query object associated with it, and that query object has
    an attribute called query_terms.

    These classes work around that assumption.
    """
    def __init__(self, *args, **kwargs):
        QuerySet.__init__(self, *args, **kwargs)
        self.query = BaseQuery()



class RHIC(Document):

    meta = {
        # Override collection name, otherwise we get r_h_i_c.
        'collection': 'rhic',
        'db_alias': 'default'
    }

    # Human readable name
    name = StringField()
    # Unique account identifier tying the RHIC to an account.
    account_id = StringField()
    # Contract associated with the RHIC.
    contract = StringField()
    # Support Level associated with the RHIC.
    support_level = StringField()
    # SLA (service level availability) associated with the RHIC.
    sla = StringField()
    # UUID associated with the RHIC.
    uuid = UUIDField()
    # List of Products associated with the RHIC.
    products = ListField()
    # List of Engineering Id's associated with the RHIC.
    engineering_ids = ListField()
    # Public cert portion of the RHIC.
    public_cert = FileField()
    # Date RHIC was created
    created_date = DateTimeField()
    # Date RHIC was last modified
    modified_date = DateTimeField()

class Product(EmbeddedDocument):

    support_level_choices = {
        'l1-l3': 'L1-L3',
        'l3': 'L3-only',
        'ss': 'SS',
    }

    sla_choices = {
        'std': 'Standard',
        'prem': 'Premium',
        'na': 'N/A',
    }

    # Product name
    name = StringField(required=True)
    # Unique product identifier
    engineering_id = IntField(required=True)
    # Quantity 
    quantity = IntField(required=True)
    # Product support level
    support_level = StringField(required=True, choices=support_level_choices.keys())
    # Product sla
    sla = StringField(required=True, choices=sla_choices.keys())
    
    meta = {'db_alias': 'default'}
    
class Contract(EmbeddedDocument):
    # Unique Contract identifier
    contract_id = StringField(unique=True, required=True)
    # List of products associated with this contract
    products = ListField(EmbeddedDocumentField(Product))
    
    meta = {'db_alias': 'default'}

class Account(Document):

    meta = {
        'queryset_class': BaseQuerySet,
        'db_alias': 'default'
    }

    # Unique account identifier
    account_id = StringField(unique=True, required=True)
    # Human readable account name
    login = StringField(unique=True, required=True)
    # List of contracts associated with the account.
    contracts = ListField(EmbeddedDocumentField(Contract)) 
    
   





