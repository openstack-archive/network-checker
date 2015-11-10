%define name network-checker
%{!?version: %define version 8.0.0}

Name: %{name}
Summary:   Network checking package for CentOS6.x
Version:   %{version}
Release:   1%{?dist}~mos8.0.0
Source0: %{name}-%{version}.tar.gz
License:   GPLv2
Obsoletes: nailgun-net-check
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL:       http://github.com/Mirantis
Requires:  vconfig
Requires:  scapy >= 2.2.0
Requires:  python-argparse
Requires:  python-pypcap >= 1.1.1
Requires:  python-cliff-tablib >= 1.0
Requires:  python-stevedore >= 1.0.0
Requires:  python-daemonize >= 1.7.3
Requires:  python-yaml >= 3.1.0
Requires:  tcpdump
Requires:  python-requests >= 2.1.0
Requires:  python-netifaces >= 0.10.4
BuildRequires: libpcap-devel
BuildRequires: python-setuptools
Conflicts: nailgun-net-check

%description
This is a network tool that helps to verify networks connectivity
between hosts in network.

%prep
%setup -cq -n %{name}-%{version}

%build
cd %{_builddir}/%{name}-%{version} && PBR_VERSION=%{version} python setup.py build

%install
cd %{_builddir}/%{name}-%{version} && PBR_VERSION=%{version} python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=%{_builddir}/%{name}-%{version}/INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{_builddir}/%{name}-%{version}/INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Wed Oct 28 2015 Vladimir Kozhukalov <vkozhukalov@mirantis.com> 8.0.0-1
- The RPM spec was extracted from fuel-web/specs/fuel-nailgun.spec
