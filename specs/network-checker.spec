%define name network-checker
%{!?version: %define version 8.0.0}

Name: %{name}
Summary:   Network checking package for CentOS
Version:   %{version}
Release:   1%{?dist}~mos8.0.0
Source0: %{name}-%{version}.tar.gz
License:   GPLv2
Obsoletes: nailgun-net-check
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL:       http://github.com/Mirantis
Requires:  scapy
%if 0%{?rhel} < 7
Requires: python-argparse
Requires: vconfig
%endif
Requires:  python-pypcap
Requires:  python-cliff-tablib
Requires:  python-stevedore
Requires:  python-daemonize
Requires:  python-yaml
Requires:  tcpdump
Requires:  python-requests
Requires:  python-netifaces
BuildRequires: libpcap-devel
BuildRequires: python-setuptools
Conflicts: nailgun-net-check

%description
This is a network tool that helps to verify networks connectivity
between hosts in network.

%prep
%setup -cq -n %{name}-%{version}

%build
cd %{_builddir}/%{name}-%{version} && python setup.py build

%install
cd %{_builddir}/%{name}-%{version} && python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=%{_builddir}/%{name}-%{version}/INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{_builddir}/%{name}-%{version}/INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Thu Nov 19 2015 Aleksandr Mogylchenko <amogylchenko@mirantis.com> 8.0.1-1
- make spec compatible with CentOS 7

* Wed Oct 28 2015 Vladimir Kozhukalov <vkozhukalov@mirantis.com> 8.0.0-1
- The RPM spec was extracted from fuel-web/specs/fuel-nailgun.spec
