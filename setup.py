#    Copyright 2014 Mirantis, Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import setuptools


setuptools.setup(
    name="network-checker",
    version='9.0.0',
    author="Mirantis Inc",
    classifiers=[
        "License :: OSI Approved :: Apache 2.0",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing"
    ],
    include_package_data=True,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'net_probe.py = network_checker.net_check.api:main',
            'fuel-netcheck = network_checker.cli:main',
            'dhcpcheck = dhcp_checker.cli:main',
            'urlaccesscheck = url_access_checker.cli:main',
        ],
        'dhcp.check': [
            'discover = dhcp_checker.commands:ListDhcpServers',
            'request = dhcp_checker.commands:ListDhcpAssignment',
            'vlans = dhcp_checker.commands:DhcpWithVlansCheck'
        ],
        'network_checker': [
            'multicast = network_checker.multicast.api:MulticastChecker',
            'simple = network_checker.tests.simple:SimpleChecker'
        ],
        'urlaccesscheck': [
            'check = url_access_checker.commands:CheckUrls',
            'with_setup = url_access_checker.commands:CheckUrlsWithSetup'
        ],
    },
)
