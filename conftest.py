#    Copyright 2015 Mirantis, Inc.
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

import os


PIDFILE = '/tmp/vde_network_checker'
IFACES = ['tap11', 'tap12']


def pytest_addoption(parser):
    parser.addoption("--vde", action='store_true', default=False,
                     help="Use vde switch for network verification.")


def pytest_configure(config):
    if config.getoption('vde'):
        base = 'vde_switch -p {pidfile} -d'.format(pidfile=PIDFILE)
        command = [base]
        taps = ['-tap {tap}'.format(tap=tap) for tap in IFACES]
        full_command = command + taps
        os.system(' '.join(full_command))
        for tap in IFACES:
            os.system('ifconfig {tap} up'.format(tap=tap))
        os.environ['NET_CHECK_IFACE_1'] = IFACES[0]
        os.environ['NET_CHECK_IFACE_2'] = IFACES[1]


def pytest_unconfigure(config):
    if os.path.exists(PIDFILE):
        with open(PIDFILE) as f:
            pid = f.read().strip()
            os.kill(int(pid), 15)
