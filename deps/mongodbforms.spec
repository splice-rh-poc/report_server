%global pkgname python-mongodbforms
%global docdir %{_docdir}/%{name}-%{version}

# Tests requiring Internet connections are disabled by default
# pass --with internet to run them (e.g. when doing a local rebuild
# for sanity checks before committing)

Name:           mongodbforms
Version:        0.1.4
Release:        1%{?dist}.splice
Summary:        An implementation of django forms using mongoengine

Group:          Development/Languages
License:        BSD
URL:            http://pypi.python.org/pypi/mongodbforms
Source0:        http://pypi.python.org/packages/source/m/mongodbforms/mongodbforms-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
Requires:       python-mongoengine


%description
This is an implementation of django's model forms for mongoengine documents.
Mongodbforms supports forms for normal documents and embedded documents.

%package doc
Summary: Documentation for %{name}
Group: Documentation

Requires: %{name} = %{version}-%{release}

%description doc
This package contains documentation for %{name}.

%files
%dir %{python_sitelib}/mongodbforms
%{python_sitelib}/mongodbforms*
%{python_sitelib}/mongodbforms/*

%files doc
%doc %{docdir}

%changelog

