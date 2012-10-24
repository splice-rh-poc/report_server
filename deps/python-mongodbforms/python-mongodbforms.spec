%global pkgname python-mongodbforms
%global docdir %{_docdir}/%{name}-%{version}

# Tests requiring Internet connections are disabled by default
# pass --with internet to run them (e.g. when doing a local rebuild
# for sanity checks before committing)

Name:           python-mongodbforms
Version:        0.1.4
Release:        4%{?dist}.splice
Summary:        An implementation of django forms using mongoengine

Group:          Development/Languages
License:        BSD
URL:            http://pypi.python.org/pypi/mongodbforms
Source0:        http://pypi.python.org/packages/source/m/mongodbforms/mongodbforms-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
Requires:       python-mongoengine
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


%description
This is an implementation of django's model forms for mongoengine documents.
Mongodbforms supports forms for normal documents and embedded documents.

%prep
%setup -q -n %{name}-%{version}


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
#rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{python_sitelib}/mongodbforms

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)

# For noarch packages: sitelib
 %{python_sitelib}/*
# For arch-specific packages: sitearch
# %{python_sitearch}/*


%changelog
* Wed Oct 24 2012 Wes Hayutin
 0.1.4-4.splice
 <whayutin@redhat.com>
- rename to python-mongodbforms

* Wed Oct 24 2012 Wes Hayutin
 0.1.4-3.splice
 <whayutin@redhat.com>
- seems to be building locally now (whayutin@redhat.com)
- another attempt to fix mongoddbforms (whayutin@redhat.com)
- trying to fix mongodbform build issue (whayutin@redhat.com)
- updated deps (whayutin@redhat.com)

* Wed Oct 24 2012 Wes Hayutin
 0.1.4-2.splice
 <whayutin@redhat.com>
- new package built with tito


