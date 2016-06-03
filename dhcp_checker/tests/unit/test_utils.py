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
import StringIO

from mock import call
from mock import patch
import unittest

from scapy import all as scapy

from dhcp_checker import utils

IP_LINK_SHOW_UP = (
    "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>"
    "mtu 1500 qdisc pfifo_fast state UP qlen 1000"
    "link/ether 08:60:6e:6f:70:09 brd ff:ff:ff:ff:ff:ff"
)

IP_LINK_SHOW_DOES_NOT_EXIST = 'Device "eth2" does not exist.'

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


class TestDhcpUtils(unittest.TestCase):

    def test_command_utils_helper(self):
        command = utils.command_util('echo', 'hello')
        self.assertEqual(command.stdout.read(), 'hello\n')

    @patch('dhcp_checker.utils.command_util')
    def test_check_iface_state_up(self, command_util):
        command_util().stdout.read.return_value = IP_LINK_SHOW_UP
        self.assertEqual(utils._iface_state('eth0'), 'UP')

    @patch('dhcp_checker.utils.command_util')
    def test_check_network_up(self, command_util):
        command_util().stdout.read.return_value = IP_LINK_SHOW_UP
        self.assertTrue(utils.check_network_up('eth0'))

    @patch('dhcp_checker.utils.command_util')
    def test_check_iface_doesnot_exist(self, command_util):
        command_util().stderr.read.return_value = IP_LINK_SHOW_DOES_NOT_EXIST
        self.assertFalse(utils.check_iface_exist('eth2'))

    @patch('dhcp_checker.utils.command_util')
    def test_check_iface_exist(self, command_util):
        command_util().stderr.read.return_value = ''
        self.assertTrue(utils.check_iface_exist('eth0'))

    @patch('dhcp_checker.utils.interfaces')
    def test_get_ifaces_exclude_lo(self, interfaces):
        interfaces.return_value = ['lo', 'eth1', 'eth2']
        self.assertEqual(utils.get_ifaces_exclude_lo(), ['eth1', 'eth2'])

    def test_filter_duplicated_results(self):
        test_data = [{'first': 'value'}, {'first': 'value'}]

        @utils.filter_duplicated_results
        def test_func(values):
            return values

        self.assertEqual(list(test_func(test_data)), [{'first': 'value'}])

    def test_filter_duplicated_results_diff(self):
        test_data = [{'first': 'value'}, {'second': 'value'}]

        @utils.filter_duplicated_results
        def test_func(values):
            return values

        self.assertEqual(list(test_func(test_data)), test_data)


class TestDhcpFormat(unittest.TestCase):

    def setUp(self):
        directory_path = os.path.dirname(__file__)
        self.scapy_data = list(scapy.rdpcap(os.path.join(directory_path,
                                                         'dhcp.pcap')))
        self.dhcp_response = self.scapy_data[1:]

    def test_single_format_decorator(self):
        """Test modifying scapy response objects

        Test verifies that single_format decorator contains logic to modify
        scapy response object into dict with predefined fields
        """

        @utils.single_format
        def tobe_decorated(iface, timeout=5):
            return [self.dhcp_response]

        self.assertEqual(tobe_decorated('eth1'), [expected_response])

    def test_order_preserver(self):
        example = {'first': 'first', 'second': 'second'}
        columns = ['second', 'first']
        items = utils.get_item_properties(example, columns)
        self.assertEqual(columns, items)


class TestMultiprocMap(unittest.TestCase):
    """Check if multiproc_map decorator works the same for different arg types

    Test verifies that working with function decorated by multiproc_map
    will work indifirently either args passed as tuple, or *args
    """

    def test_multiproc_map_first_tuple(self):

        @utils.multiproc_map
        def test_multiproc(*args, **kwargs):
            return args, kwargs

        rargs, rkwargs = test_multiproc(('h', 'e'))
        self.assertEqual(rargs, ('h', 'e'))
        self.assertEqual(rkwargs, {})

    def test_multiproc_mapn_normal(self):

        @utils.multiproc_map
        def test_multiproc(*args, **kwargs):
            return args, kwargs

        rargs, rkwargs = test_multiproc('h', 'e')
        self.assertEqual(rargs, ('h', 'e'))
        self.assertEqual(rkwargs, {})


@patch('dhcp_checker.utils._iface_state')
@patch('dhcp_checker.utils.command_util')
class TestIfaceStateHelper(unittest.TestCase):

    def test_iface_is_up(self, command, iface_state):
        iface_value = iter(('UP',) * 2)
        iface_state.side_effect = lambda *args, **kwargs: next(iface_value)
        with utils.IfaceState(['eth1'], wait_up=0) as ifaces:
            self.assertEqual(ifaces[0], 'eth1')
        self.assertEqual(iface_state.call_count, 2)
        self.assertEqual(command.call_count, 0)

    def test_iface_is_down(self, command, iface_state):
        iface_value = iter(('DOWN', 'DOWN', 'UP', 'UP'))
        iface_state.side_effect = lambda *args, **kwargs: next(iface_value)
        with utils.IfaceState(['eth1'], wait_up=10) as ifaces:
            self.assertEqual(ifaces[0], 'eth1')
        self.assertEqual(iface_state.call_count, 4)
        self.assertEqual(command.call_count, 2)
        self.assertEqual(command.call_args_list,
                         [call('ip', 'link', 'set', 'dev', 'eth1', 'up'),
                          call('ip', 'link', 'set', 'dev', 'eth1', 'down')])

    def test_iface_cant_ifup(self, command, iface_state):
        iface_value = iter(('DOWN',) * 10)
        iface_state.side_effect = lambda *args, **kwargs: next(iface_value)

        with patch('sys.stderr', new=StringIO.StringIO()) as stderr_mock:
            with utils.IfaceState(['eth1'], wait_up=5) as ifaces:
                self.assertEqual(ifaces[0], 'eth1')

        self.assertEquals(
            stderr_mock.getvalue(), 'Tried my best to ifup iface eth1.')
        self.assertEquals(command.call_count, 1)
