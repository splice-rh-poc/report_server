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

from sreport.api import ProductUsageResource

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
    (r'^ui/login/$', 'sreport.views.login'),
    (r'^ui/logout/$', 'sreport.views.logout'),
    (r'^ui/$', 'sreport.views.index'),
    (r'^ui/index$', 'sreport.views.index'),
    (r'^ui/create_report/$', 'sreport.views.create_report'),
    (r'^ui/report/$', 'sreport.views.report'),
    (r'^ui/import/$', 'sreport.views.import_checkin_data'),
    (r'^ui/report/details/$', 'sreport.views.detailed_report'),
    (r'^ui/report/details/instance_details/$', 'sreport.views.instance_report'),
    (r'^ui/ui20/$', 'sreport.views.ui20'),
    (r'^ui/ui20/index/$', 'sreport.views.index_ui20'),
    (r'^ui/ui20/import/$', 'sreport.views.import_ui20'),
    (r'^ui/ui20/login/$', 'sreport.views.login_ui20'),
    (r'^ui/ui20/logout/$', 'sreport.views.logout_ui20'),
    (r'^ui/ui20/report_form/$', 'sreport.views.report_form_ui20'),
    (r'^ui/ui20/report/$', 'sreport.views.report_ui20'),
    (r'^ui/ui20/details/$', 'sreport.views.detailed_report_ui20'),
    (r'^ui/ui20/max_report/$', 'sreport.views.max_report'),
    (r'^ui/ui20/instance_details/$', 'sreport.views.instance_detail_ui20'),
)

urlpatterns += (
    # API Resources
    url(r'^api/', include(v1_api.urls)),
)


