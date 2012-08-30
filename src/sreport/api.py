from sreport.models import ProductUsage
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS


class ProductUsageResource(ModelResource):
    class Meta:
        queryset = ProductUsage.consumer

