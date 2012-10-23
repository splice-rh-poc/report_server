# report-server package -------------------------------------------------------
Name:		report-server
Version:	0.5
Release:	1%{?dist}
Summary:	Reporting server for reporting RHIC net aggregate usage.

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
Requires:   %{name}-common = %{version}-%{release}


%description
Reporting server for reporting RHIC net aggregate usage.


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

# Remove egg info
rm -rf %{buildroot}/%{python_sitelib}/*.egg-info


%files 
%defattr(-,root,root,-)
%{python_sitelib}/report_server
%defattr(-,apache,apache,-)
%{_usr}/lib/report_server
%{_localstatedir}/www/html/report_server
 

%files common
%defattr(-,root,root,-)
%{python_sitelib}/report_server/common
%{python_sitelib}/report_server/__init__.py*

%files import
%defattr(-,root,root,-)
%{python_sitelib}/report_server/report_import
%defattr(-,apache,apache,-)
%{_usr}/lib/report_server/report_import


%clean
rm -rf %{buildroot}


%changelog
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


