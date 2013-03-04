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


from django.conf.urls import patterns, include, url
from django.views.generic import list_detail
from report_server.sreport.api import ProductUsageResource, \
    QuarantinedDataResource, ComplianceDataResource, ReportResource, SpliceServerResourceMod
from tastypie.api import Api

v1_api = Api(api_name='v1')

# Resources
productusage_resource = ProductUsageResource()
quarantine_resource = QuarantinedDataResource()
compliance_resource = ComplianceDataResource()
report_resource = ReportResource()

v1_api.register(productusage_resource)
v1_api.register(quarantine_resource)
v1_api.register(compliance_resource)
v1_api.register(report_resource)
v1_api.register(SpliceServerResourceMod())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'splice_reports.views.home', name='home'),
    # url(r'^splice_reports/', include('splice_reports.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),

    (r'^meter/$', 'report_server.sreport.views.start_meter'),
    (r'^meter/index/$', 'report_server.sreport.views.index'),
    (r'^meter/import/$', 'report_server.sreport.views.execute_import'),
    (r'^meter/login/$', 'report_server.sreport.views.login'),
    (r'^meter/logout/$', 'report_server.sreport.views.logout'),
    (r'^meter/report_form/$', 'report_server.sreport.meter.views.report_form'),
    (r'^meter/space_form/$', 'report_server.sreport.views.space_form'),
    (r'^meter/report_form_rhics/$', 'report_server.sreport.views.report_form_rhics'),
    (r'^meter/report/$', 'report_server.sreport.meter.views.report'),
    (r'^meter/default_report/$', 'report_server.sreport.views.default_report'),
    (r'^meter/export/$', 'report_server.sreport.views.export'),
    (r'^meter/details/$', 'report_server.sreport.views.detailed_report'),
    (r'^meter/max_report/$', 'report_server.sreport.views.max_report'),
    (r'^meter/quarantine/$', 'report_server.sreport.views.quarantined_report'),
    (r'^meter/fact_compliance/$', 'report_server.sreport.views.system_fact_compliance'),
    (r'^meter/instance_details/$', 'report_server.sreport.views.instance_detail'),
    
    (r'^space/$', 'report_server.sreport.views.start_space'),
    (r'^space/report_form/$', 'report_server.sreport.spacewalk.views.report_form'),
)

urlpatterns += (
    # API Resources
    url(r'^api/', include(v1_api.urls)),
)


