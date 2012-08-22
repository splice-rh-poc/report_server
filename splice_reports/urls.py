from django.conf.urls import patterns, include, url
from django.views.generic import list_detail
from sreport.views import pulisting


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'splice_reports.views.home', name='home'),
    # url(r'^splice_reports/', include('splice_reports.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^report/$', pulisting),
    (r'^ui/$', 'sreport.views.index'),
    (r'^ui/create/$', 'sreport.views.create'),
)
