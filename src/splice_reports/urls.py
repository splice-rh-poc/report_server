from django.conf.urls import patterns, include, url
from django.views.generic import list_detail



# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'splice_reports.views.home', name='home'),
    # url(r'^splice_reports/', include('splice_reports.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    (r'^ui/login/$', 'sreport.views.login'),
    (r'^ui/logout/$', 'sreport.views.logout'),
    (r'^ui/$', 'sreport.views.index'),
    (r'^ui/index$', 'sreport.views.index'),
    (r'^ui/create_report/$', 'sreport.views.create_report'),
    (r'^ui/report/$', 'sreport.views.report'),
    (r'^ui/import/$', 'sreport.views.import_checkin_data'),
    (r'^ui/report/details/$', 'sreport.views.detailed_report'),
    (r'^ui/report/details/instance_details/$', 'sreport.views.instance_report'),
    (r'^ui/admin/$', 'sreport.views.admin'),
    (r'^ui/admin/index/$', 'sreport.views.index_admin'),
    (r'^ui/admin/import/$', 'sreport.views.import_admin'),
    (r'^ui/admin/login/$', 'sreport.views.login_admin'),
    (r'^ui/admin/logout/$', 'sreport.views.logout_admin'),
    (r'^ui/admin/report_form/$', 'sreport.views.report_form_admin'),
    (r'^ui/admin/report/$', 'sreport.views.report_admin'),
    (r'^ui/admin/details/$', 'sreport.views.detailed_report_admin'),
    (r'^ui/admin/instance_details/$', 'sreport.views.instance_detail_admin'),
    (r'^ui/foo/$', 'sreport.views.foo'),
)
