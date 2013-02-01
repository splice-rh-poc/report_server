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

from tastypie.api import Api

from report_server.sreport.api import ProductUsageResource, QuarantinedDataResource, ComplianceDataResource, \
                                    ReportResource

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

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'splice_reports.views.home', name='home'),
    # url(r'^splice_reports/', include('splice_reports.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),

    (r'^report-server/meter/$', 'report_server.sreport.views.start_meter'),
    (r'^report-server/meter/index/$', 'report_server.sreport.views.index'),
    (r'^report-server/meter/import/$', 'report_server.sreport.views.execute_import'),
    (r'^report-server/meter/login/$', 'report_server.sreport.views.login'),
    (r'^report-server/meter/logout/$', 'report_server.sreport.views.logout'),
    (r'^report-server/meter/report_form/$', 'report_server.sreport.meter.views.report_form'),
    (r'^report-server/meter/report_form_rhics/$', 'report_server.sreport.views.report_form_rhics'),
    (r'^report-server/meter/report/$', 'report_server.sreport.views.report'),
    (r'^report-server/meter/default_report/$', 'report_server.sreport.views.default_report'),
    (r'^report-server/meter/export/$', 'report_server.sreport.views.export'),
    (r'^report-server/meter/details/$', 'report_server.sreport.views.detailed_report'),
    (r'^report-server/meter/max_report/$', 'report_server.sreport.views.max_report'),
    (r'^report-server/meter/quarantine/$', 'report_server.sreport.views.quarantined_report'),
    (r'^report-server/meter/fact_compliance/$', 'report_server.sreport.views.system_fact_compliance'),
    (r'^report-server/meter/instance_details/$', 'report_server.sreport.views.instance_detail'),
    
    (r'^report-server/space/$', 'report_server.sreport.views.start_space'),
    (r'^report-server/space/report_form/$', 'report_server.sreport.spacewalk.views.report_form'),
)

urlpatterns += (
    # API Resources
    url(r'^api/', include(v1_api.urls)),
)


