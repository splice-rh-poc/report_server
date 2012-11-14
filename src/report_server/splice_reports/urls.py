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

from report_server.sreport.api import ProductUsageResource

v1_api = Api(api_name='v1')

# Resources
productusage_resource = ProductUsageResource()
v1_api.register(productusage_resource)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'splice_reports.views.home', name='home'),
    # url(r'^splice_reports/', include('splice_reports.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),

    (r'^ui20/$', 'report_server.sreport.views.ui20'),
    (r'^ui20/index/$', 'report_server.sreport.views.index_ui20'),
    (r'^ui20/import/$', 'report_server.sreport.views.import_ui20'),
    (r'^ui20/login/$', 'report_server.sreport.views.login_ui20'),
    (r'^ui20/logout/$', 'report_server.sreport.views.logout_ui20'),
    (r'^ui20/report_form/$', 'report_server.sreport.views.report_form_ui20'),
    (r'^ui20/report/$', 'report_server.sreport.views.report_ui20'),
    (r'^ui20/export/$', 'report_server.sreport.views.export'),
    (r'^ui20/details/$', 'report_server.sreport.views.detailed_report_ui20'),
    (r'^ui20/max_report/$', 'report_server.sreport.views.max_report'),
    (r'^ui20/quarantine/$', 'report_server.sreport.views.quarantined_report'),
    (r'^report-server/ui20/fact_compliance/$', 'report_server.sreport.views.systemFactCompliance'),
    (r'^ui20/instance_details/$', 'report_server.sreport.views.instance_detail_ui20'),
)

urlpatterns += (
    # API Resources
    url(r'^api/', include(v1_api.urls)),
)


