#    Copyright 2013 Mirantis, Inc.
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

import functools
import re
import subprocess
import sys
import time

from netifaces import interfaces
from scapy import all as scapy


DHCP_OFFER_COLUMNS = ('iface', 'mac', 'server_ip', 'server_id', 'gateway',
                      'dport', 'message', 'yiaddr')


def command_util(*command):
    """object with stderr and stdout"""
    return subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


def _check_vconfig():
    """Check vconfig installed or not"""
    return not command_util('which', 'vconfig').stderr.read()


def _iface_state(iface):
    """For a given iface return it's state

    returns UP, DOWN, UNKNOWN
    """
    state = command_util('ip', 'link', 'show', iface).stdout.read()
    search_result = re.search(r'.*<(?P<state>.*)>.*', state)
    if search_result:
        state_list = search_result.groupdict().get('state', [])
        if 'UP' in state_list:
            return 'UP'
        else:
            return 'DOWN'
    return 'UNKNOWN'


def check_network_up(iface):
    return _iface_state(iface) == 'UP'


def check_iface_exist(iface):
    """Check provided interface exists"""
    return not command_util("ip", "link", "show", iface).stderr.read()


def filtered_ifaces(ifaces):
    for iface in ifaces:
        if not check_iface_exist(iface):
            sys.stderr.write('Iface {0} does not exist.'.format(iface))
        else:
            if not check_network_up(iface):
                sys.stderr.write('Network for iface {0} is down.'.format(
                    iface))
            else:
                yield iface


def get_ifaces_exclude_lo():
    ifaces = interfaces()
    if 'lo' in ifaces:
        ifaces.remove('lo')
    return ifaces


def pick_ip(range_start, range_end):
    """Given start_range, end_range generate list of ips

    >>> next(pick_ip('192.168.1.10','192.168.1.13'))
    '192.168.1.10'
    """
    split_address = lambda ip_address: \
        [int(item) for item in ip_address.split('.')]
    range_start = split_address(range_start)
    range_end = split_address(range_end)
    i = 0
    # ipv4 subnet cant be longer that 4 items
    while i < 4:
        # 255 - end of subnet
        if not range_start[i] == range_end[i] and range_start[i] < 255:
            yield '.'.join([str(item) for item in range_start])
            range_start[i] += 1
        else:
            i += 1


def get_item_properties(item, columns):
    """Get specified in columns properties, with preserved order.

    Required for correct cli table generation

    :param item: dict
    :param columns: list with arbitrary keys
    """
    properties = []
    for key in columns:
        properties.append(item.get(key, ''))
    return properties


def format_options(options):
    """Util for serializing dhcp options

    @options = [1,2,3]
    >>> format_options([1, 2, 3])
    '\x01\x02\x03'
    """
    return "".join((chr(item) for item in options))


def _dhcp_options(dhcp_options):
    """Dhcp options returned by scapy is not in usable format

    [('message-type', 2), ('server_id', '192.168.0.5'),
        ('name_server', '192.168.0.1', '192.168.0.2'), 'end']
    """
    for option in dhcp_options:
        if isinstance(option, (tuple, list)):
            header = option[0]
            if len(option[1:]) > 1:
                yield (header, option)
            else:
                yield (header, option[1])


def format_answer(ans, iface):
    dhcp_options = dict(_dhcp_options(ans[scapy.DHCP].options))
    results = (
        iface, ans[scapy.Ether].src, ans[scapy.IP].src,
        dhcp_options['server_id'], ans[scapy.BOOTP].giaddr,
        ans[scapy.UDP].sport,
        scapy.DHCPTypes[dhcp_options['message-type']],
        ans[scapy.BOOTP].yiaddr)
    return dict(zip(DHCP_OFFER_COLUMNS, results))


def single_format(func):
    """Manage format of dhcp response"""
    @functools.wraps(func)
    def formatter(*args, **kwargs):
        iface = args[0]
        ans = func(*args, **kwargs)
        # scapy stores all sequence of requests
        # so ans[0][1] would be response to first request
        return [format_answer(response[1], iface) for response in ans]
    return formatter


def multiproc_map(func):
    # multiproc map could not work with format *args
    @functools.wraps(func)
    def workaround(*args, **kwargs):
        args = args[0] if isinstance(args[0], (tuple, list)) else args
        return func(*args, **kwargs)
    return workaround


def filter_duplicated_results(func):
    # due to network infra on broadcast multiple duplicated results
    # returned. This helper filter them out
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        return (dict(t) for t in set([tuple(d.items()) for d in resp]))
    return wrapper


class VlansContext(object):
    """Contains all logic to manage vlans"""

    def __init__(self, config):
        """Initialize VlansContext

        @config - list or tuple of (iface, vlan) pairs
        """
        self.config = config

    def __enter__(self):
        for iface, vlans in self.config.iteritems():
            vifaces = []
            for vlan in vlans:
                if vlan > 0:
                    vifaces.append('{0}.{1}'.format(iface, vlan))
            yield str(iface), vifaces

    def __exit__(self, type, value, trace):
        pass


class IfaceState(object):
    """Context manager to control state of ifaces while dhcp checker runs"""

    def __init__(self, ifaces, rollback=True, wait_up=30):
        self.rollback = rollback
        self.wait_up = wait_up
        self.ifaces = ifaces
        self.pre_ifaces_state = self.get_ifaces_state()

    def get_ifaces_state(self):
        state = {}
        for iface in self.ifaces:
            state[iface] = _iface_state(iface)
        return state

    def iface_up(self, iface):
        if _iface_state(iface) != 'UP':
            command_util('ip', 'link', 'set', 'dev', iface, 'up')

            deadline = time.time() + self.wait_up
            while time.time() < deadline:
                if _iface_state(iface) == 'UP':
                    break
                time.sleep(1)
            else:
                sys.stderr.write(
                    'Tried my best to ifup iface {0}.'.format(iface))

    def __enter__(self):
        for iface in self.ifaces:
            self.iface_up(iface)
        return self.ifaces

    def __exit__(self, exc_type, exc_val, exc_tb):
        for iface in self.ifaces:
            if self.pre_ifaces_state[iface] != 'UP' \
                    and _iface_state(iface) == 'UP' and self.rollback:
                command_util('ip', 'link', 'set', 'dev', iface, 'down')


def create_mac_filter(iface):
    """tcpdump can not catch all 6 octets so it is splitted

    See http://blog.jasonantman.com/2010/04/dhcp-debugging-and-handy-tcpdump-filters # noqa
    """
    mac = scapy.get_if_hwaddr(iface).split(':')
    filter1 = '(udp[36:2] = 0x{0})'.format(''.join(mac[:2]))
    filter2 = '(udp[38:4] = 0x{0})'.format(''.join(mac[2:]))
    return '{0} and {1}'.format(filter1, filter2)
