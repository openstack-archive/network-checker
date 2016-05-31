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

import os
import unittest

from mock import patch
from scapy import all as scapy

from dhcp_checker import api

dhcp_options = [("message-type", "offer"), "end"]

request = (
    scapy.Ether(),
    scapy.Ether(src="", dst="ff:ff:ff:ff:ff:ff") /
    scapy.IP(src="0.0.0.0", dst="255.255.255.255") /
    scapy.UDP(sport=68, dport=67) /
    scapy.BOOTP(chaddr="") /
    scapy.DHCP(options=dhcp_options)
)

expected_response = {
    'dport': 67,
    'gateway': '172.18.194.2',
    'iface': 'eth1',
    'mac': '00:15:17:ee:0a:a8',
    'message': 'offer',
    'server_id': '172.18.208.44',
    'server_ip': '172.18.194.2',
    'yiaddr': '172.18.194.35'
}


class IfaceStateMock(object):

    def __init__(self, ifaces):
        self.ifaces = ifaces

    def __enter__(self):
        return self.ifaces

    def __exit__(self, exc_type, exc_val, ex_tb):
        pass


@patch('dhcp_checker.utils.IfaceState', new=IfaceStateMock)
class TestDhcpApi(unittest.TestCase):

    def setUp(self):
        directory_path = os.path.dirname(__file__)
        self.scapy_data = list(scapy.rdpcap(os.path.join(directory_path,
                                                         'dhcp.pcap')))
        self.dhcp_response = self.scapy_data[1:]

    @patch('dhcp_checker.api.scapy.srp')
    @patch('dhcp_checker.api.scapy.get_if_raw_hwaddr')
    def test_check_dhcp_on_eth(self, raw_hwaddr, srp_mock, *_):
        raw_hwaddr.return_value = ('111', '222')
        srp_mock.return_value = ([self.dhcp_response], [])
        response = api.check_dhcp_on_eth('eth1', timeout=5)
        self.assertEqual([expected_response], response)

    @patch('dhcp_checker.api.scapy.srp')
    @patch('dhcp_checker.api.scapy.get_if_raw_hwaddr')
    def test_check_dhcp_on_eth_empty_response(self, raw_hwaddr, srp_mock, *_):
        raw_hwaddr.return_value = ('111', '222')
        srp_mock.return_value = ([], [])
        response = api.check_dhcp_on_eth('eth1', timeout=5)
        self.assertEqual([], response)


    @patch('dhcp_checker.utils.filtered_ifaces')
    @patch('dhcp_checker.api.send_dhcp_discover')
    @patch('dhcp_checker.api.make_listeners')
    def test_check_dhcp_with_multiple_ifaces(
            self, make_listeners, send_discover, filtered_ifaces, *_):
        repeat = 1
        ifaces = ['eth1', 'eth2']

        filtered_ifaces.return_value = ifaces

        api.check_dhcp(ifaces, repeat=repeat)

        make_listeners.assert_called_once_with(('eth2', 'eth1'))
        self.assertEqual(filtered_ifaces.call_count, repeat)
        self.assertEqual(send_discover.call_count, 2)

    @patch('dhcp_checker.utils.filtered_ifaces')
    @patch('dhcp_checker.api.send_dhcp_discover')
    @patch('dhcp_checker.api.make_listeners')
    def test_check_dhcp_with_vlans(self, make_listeners,
                                   send_discover, filtered_ifaces, *_):
        config_sample = {
            'eth0': (100, 101),
            'eth1': (100, 102)
        }
        ifaces_to_check = ['eth1', 'eth0',
                           'eth1.100', 'eth1.102',
                           'eth0.100', 'eth0.101']
        filtered_ifaces.return_value = ifaces_to_check
        api.check_dhcp_with_vlans(config_sample, timeout=1, repeat=1,
                                  w_vlans=True)
        make_listeners.assert_called_once_with(('eth1', 'eth0'))
        self.assertEqual(send_discover.call_count, 6)

    @patch('dhcp_checker.api.time.sleep')
    @patch('dhcp_checker.api.send_dhcp_discover')
    @patch('dhcp_checker.api.make_listeners')
    def test_check_dhcp_with_vlans_repeat_2(self, make_listeners,
                                            send_discover, sleep_mock, *_):
        config_sample = {
            'eth0': (),
        }
        api.check_dhcp_with_vlans(config_sample, timeout=1, repeat=3)
        self.assertEqual(sleep_mock.call_count, 3)
        make_listeners.assert_called_once_with(('eth0',))
        self.assertEqual(send_discover.call_count, 3)

    @patch('dhcp_checker.api.utils.filtered_ifaces')
    @patch('dhcp_checker.api.get_ifaces_exclude_lo')
    @patch('dhcp_checker.api.send_dhcp_discover')
    @patch('dhcp_checker.api.make_listeners')
    def test_check_dhcp_with_no_ifaces(
            self, make_listeners, send_discover, interfaces,
            filtered_ifaces, *_):
        interfaces.return_value = ['eth1']
        filtered_ifaces.return_value = ['eth1']
        api.check_dhcp(None, timeout=1, repeat=2)
        make_listeners.assert_called_once_with(('eth1',))
        self.assertEqual(send_discover.call_count, 2)
