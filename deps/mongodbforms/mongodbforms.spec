%global pkgname python-mongodbforms
%global docdir %{_docdir}/%{name}-%{version}

# Tests requiring Internet connections are disabled by default
# pass --with internet to run them (e.g. when doing a local rebuild
# for sanity checks before committing)

Name:           mongodbforms
Version:        0.1.4
Release:        2%{?dist}.splice
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

%package doc
Summary: Documentation for %{name}
Group: Documentation

Requires: %{name} = %{version}-%{release}

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

%description doc
This package contains documentation for %{name}.

%files
%dir %{python_sitelib}/mongodbforms
%{python_sitelib}/mongodbforms*
%{python_sitelib}/mongodbforms/*

%files doc
%doc %{docdir}

%changelog
* Wed Oct 24 2012 Wes Hayutin
 0.1.4-2.splice
 <whayutin@redhat.com>
- new package built with tito


