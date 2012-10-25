# report-server package -------------------------------------------------------
Name:		report-server
Version:	0.17
Release:	1%{?dist}
Summary:	Reporting server for Splice.

Group:		Development/Languages
License:	GPLv2+
URL:		https://github.com/splice/report_server
Source0:	%{name}-%{version}.tar.gz

BuildRequires:	python-setuptools
BuildRequires:  python2-devel

Requires:   mongodb-server
Requires:   pymongo
Requires:   httpd
Requires:   mod_wsgi
Requires:   mod_ssl
Requires:   python-isodate
Requires:   Django
Requires:   python-django-tastypie
Requires:   python-django-tastypie-mongoengine
Requires:   python-mongoengine
Requires:   python-mongodbforms
Requires:   pymongo-gridfs
Requires:   %{name}-common = %{version}-%{release}


%description
Reporting server for Splice.


# report-server import package ------------------------------------------------
%package import
Summary:    Reporting server import application
Group:		Development/Languages

Requires:   mongodb-server
Requires:   pymongo
Requires:   httpd
Requires:   mod_wsgi
Requires:   mod_ssl
Requires:   python-bson
Requires:   python-isodate
Requires:   Django
Requires:   python-django-tastypie
Requires:   python-django-tastypie-mongoengine
Requires:   python-mongoengine
Requires:   %{name}-common = %{version}-%{release}


%description import
Reporting server import application


%package common
Summary:    Common libraries for report-server.
Group:      Development/Languages

%description common
Common libraries for report-server.

%prep
%setup -q


%build
pushd src
%{__python} setup.py build
popd


%install
rm -rf %{buildroot}
pushd src
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd
mkdir -p %{buildroot}/%{_sysconfdir}/httpd/conf.d/
mkdir -p %{buildroot}/%{_var}/log/%{name}
mkdir -p %{buildroot}/%{_usr}/lib/report_server
mkdir -p %{buildroot}/%{_localstatedir}/www/html/report_server/
mkdir -p /var/log/%{name}


# Install source
pushd src
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd

# Install template files
mkdir -p %{buildroot}/%{_usr}/lib/report_server/report_import
cp -R src/report_server/templates %{buildroot}/%{_usr}/lib/report_server
cp -R src/report_server/report_import/templates %{buildroot}/%{_usr}/lib/report_server/report_import

# Install static files
mkdir -p %{buildroot}/%{_localstatedir}/www/html/report_server/sreport
cp -R src/report_server/sreport/static %{buildroot}/%{_localstatedir}/www/html/report_server/sreport

# Install WSGI script & httpd conf
cp -R srv %{buildroot}
cp etc/httpd/conf.d/%{name}.conf %{buildroot}/%{_sysconfdir}/httpd/conf.d/

# Remove egg info
rm -rf %{buildroot}/%{python_sitelib}/*.egg-info


%files 
%defattr(-,root,root,-)
%{python_sitelib}/report_server
%defattr(-,apache,apache,-)
%{_usr}/lib/report_server
%{_localstatedir}/www/html/report_server
%dir /srv/%{name}
%dir /var/log/%{name}
/srv/%{name}/webservices.wsgi
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
 

%files common
%defattr(-,root,root,-)
%{python_sitelib}/report_server/common
%{python_sitelib}/report_server/__init__.py*

%files import
%defattr(-,root,root,-)
%{python_sitelib}/report_server/report_import
%defattr(-,apache,apache,-)
%{_usr}/lib/report_server/report_import


#%clean
#rm -rf %{buildroot}

#%doc

%changelog
* Wed Oct 24 2012 Wes Hayutin
 0.17-1
 <whayutin@redhat.com>
- additional changes for packaging (whayutin@redhat.com)
- Automatic commit of package [python-mongodbforms] minor release
  [0.1.4-7.splice]. (whayutin@redhat.com)
- update prep step for proper build root name (whayutin@redhat.com)
- Automatic commit of package [python-mongodbforms] minor release
  [0.1.4-6.splice]. (whayutin@redhat.com)
- update build root (whayutin@redhat.com)
- Automatic commit of package [python-mongodbforms] minor release
  [0.1.4-5.splice]. (whayutin@redhat.com)
- getting a bad exit code from a %%clean (whayutin@redhat.com)
- Automatic commit of package [python-mongodbforms] minor release
  [0.1.4-4.splice]. (whayutin@redhat.com)

* Wed Oct 24 2012 Wes Hayutin
 0.16-1
 <whayutin@redhat.com>
- since mongdbforms requires python-mongoengine.. renaming to python-
  mongodbforms, and making reports require it (whayutin@redhat.com)
- Automatic commit of package [mongodbforms] minor release [0.1.4-3.splice].
  (whayutin@redhat.com)
- seems to be building locally now (whayutin@redhat.com)

* Wed Oct 24 2012 Wes Hayutin
 0.15-1
 <whayutin@redhat.com>
- another attempt to fix mongoddbforms (whayutin@redhat.com)
- trying to fix mongodbform build issue (whayutin@redhat.com)
- updated deps (whayutin@redhat.com)
- Automatic commit of package [mongodbforms] minor release [0.1.4-2.splice].
  (whayutin@redhat.com)
- adding dep source for mongodbforms (whayutin@redhat.com)

* Wed Oct 24 2012 Wes Hayutin
 0.14-1
 <whayutin@redhat.com>
- most of the packaging is complete (whayutin@redhat.com)
- Automatic commit of package [report-server] release [0.13-1].
  (whayutin@redhat.com)

* Wed Oct 24 2012 Wes Hayutin
 0.13-1
 <whayutin@redhat.com>
- fixed imports for packaging (whayutin@redhat.com)

* Tue Oct 23 2012 Wes Hayutin <whayutin@redhat.com> 0.12-1
- changing wsgi name from splice_reports to report-server (whayutin@redhat.com)

* Tue Oct 23 2012 Wes Hayutin <whayutin@redhat.com> 0.11-1
- fix to initial page load, and spec (whayutin@redhat.com)

* Tue Oct 23 2012 Wes Hayutin <whayutin@redhat.com> 0.10-1
- rename srv dir (whayutin@redhat.com)

* Tue Oct 23 2012 Wes Hayutin <whayutin@redhat.com> 0.9-1
- missing files in spec (whayutin@redhat.com)

* Tue Oct 23 2012 Wes Hayutin <whayutin@redhat.com> 0.8-1
- fixed naming for http conf (whayutin@redhat.com)

* Tue Oct 23 2012 Wes Hayutin <whayutin@redhat.com> 0.7-1
- updated packaging (whayutin@redhat.com)
- created a control to prevent imports from stepping on each other
  (whayutin@redhat.com)
- adding rules to production settings.py (whayutin@redhat.com)

* Tue Oct 23 2012 Wes Hayutin <whayutin@redhat.com> 0.6-1
- merge (whayutin@redhat.com)
- fix model change from splice server (whayutin@redhat.com)
- update unit tests (whayutin@redhat.com)
- couple things to clean up (whayutin@redhat.com)
- rename from admin -> ui20 (whayutin@redhat.com)
- added functionality to gray out tab(s) before it can be used moved foo folder
  to admin modified url and view methods to accomodate the move
  (dgao@redhat.com)
- added MongoEncoder and helper methods to jsonify objs (dgao@redhat.com)
- first pass at max daily usage (whayutin@redhat.com)
- updated import for new splice server model (whayutin@redhat.com)
- merge in selinux rules (whayutin@redhat.com)
- added copyright info and graph data (whayutin@redhat.com)
- changed width of graph to occupy 100%% of the existing content space
  (dgao@redhat.com)
- remove debug code (dgao@redhat.com)
- added charting lib for Max Data tab (dgao@redhat.com)
- stubbed out max daily usage (whayutin@redhat.com)
- begin max page (whayutin@redhat.com)
- merge (whayutin@redhat.com)
- minor fixes (whayutin@redhat.com)
- don't reset form after report is generated. added reset button clear out
  report/detail pane if reset button is clicked (dgao@redhat.com)
- added to_dict() to ReportData and ReportDataDaily (dgao@redhat.com)
- fixed import issue (albeit, not very elegant) (dgao@redhat.com)
- fixing import issue (whayutin@redhat.com)
- removed unused files (dgao@redhat.com)
- merge (whayutin@redhat.com)
- had to move foo templates, removed some bad tests, fixed an import in views
  (whayutin@redhat.com)
- intermediate checkin for more fixes from the merge (dgao@redhat.com)
- moved files to the correct location after merge (dgao@redhat.com)
- Merge branch 'master' of git://github.com/segfault923/report_server into
  UI_20 (dgao@redhat.com)
- finished off instance_detail (dgao@redhat.com)
- intermediate changes for instance_detail work initial revision for todo list
  (dgao@redhat.com)
- minor deletion of unused code (dgao@redhat.com)
- added reporting and detail pane (dgao@redhat.com)
- initial revision to centralize everything to one admin page (dgao@redhat.com)

* Fri Oct 19 2012 John Matthews <jmatthews@redhat.com> 0.5-1
- Add requires for 'report-server-common' to 'report-server-import'
  (jmatthews@redhat.com)

* Fri Oct 19 2012 John Matthews <jmatthews@redhat.com> 0.4-1
- Small tweaks to productusage.py after some testing (jmatthews@redhat.com)
- Created a report-server-common RPM, currently it just packages
  report_server/__init__.py this allows report-server-import to function by
  itself (jmatthews@redhat.com)
- Update json parsing to run on el6, might need to revisit for Fedora
  (jmatthews@redhat.com)
- mdu tests need to removed atm (whayutin@redhat.com)
- added max daily usage calulation and unit tests (whayutin@redhat.com)
- broke out unit tests, finished configurable import, added generated to
  instance details page (whayutin@redhat.com)
- removed old count def in products, added tests, refactored how biz rules are
  read in (whayutin@redhat.com)
- fix for hudson path (whayutin@redhat.com)
- finished first pass at custom config (whayutin@redhat.com)
- fix python path for dev settings (whayutin@redhat.com)
- first pass at biz rules as config (whayutin@redhat.com)
- adding custom count (whayutin@redhat.com)
- jboss is <=4 (whayutin@redhat.com)
- change default report settings for splice/report.conf (whayutin@redhat.com)
- missed one import (whayutin@redhat.com)
- missed one import (whayutin@redhat.com)
- fix imports (whayutin@redhat.com)
- reworked batch import, cleaned templates, added logout, cleaned imports
  (whayutin@redhat.com)
- Merge branch 'master' of github.com:splice/report_server
  (whayutin@redhat.com)
- Remove unneeded lines (jslagle@redhat.com)
- Add Requires (jslagle@redhat.com)
- Merge branch 'master' of github.com:splice/report_server
  (whayutin@redhat.com)
- Merge branch 'master' of github.com:splice/report_server merge of updated
  import (whayutin@redhat.com)
- more tests (whayutin@redhat.com)

* Fri Oct 05 2012 James Slagle <jslagle@redhat.com> 0.3-1
- Packaging fixes (jslagle@redhat.com)
- Install all src under a top level report_server directory
  (jslagle@redhat.com)
- Fix file installation path (jslagle@redhat.com)

* Fri Oct 05 2012 James Slagle <jslagle@redhat.com> 0.2-1
- new package built with tito


