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

import json
from mock import patch
import unittest

from dhcp_checker import cli

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


@patch('dhcp_checker.commands.api')
class TestCommandsInterface(unittest.TestCase):

    def test_list_dhcp_servers(self, api):
        api.check_dhcp.return_value = iter([expected_response])
        command = cli.main(['discover', '--ifaces', 'eth0', 'eth1',
                            '--format', 'json'])
        self.assertEqual(command, 0)
        api.check_dhcp.assert_called_once_with(['eth0', 'eth1'],
                                               repeat=2, timeout=5)

    def test_list_dhcp_assignment(self, api):
        api.check_dhcp_request.return_value = iter([expected_response])
        command = cli.main(['request', 'eth1', '10.20.0.2',
                            '--range_start', '10.20.0.10',
                            '--range_end', '10.20.0.20'])
        self.assertEqual(command, 0)
        api.check_dhcp_request.assert_called_once_with(
            'eth1', '10.20.0.2', '10.20.0.10', '10.20.0.20', timeout=5
        )

    def test_list_dhcp_vlans_info(self, api):
        config_sample = {'eth1': ['100', '101'],
                         'eth2': range(103, 110)}
        api.check_dhcp_with_vlans.return_value = iter([expected_response])
        command = cli.main(['vlans', json.dumps(config_sample)])
        self.assertEqual(command, 0)
        api.check_dhcp_with_vlans.assert_called_once_with(
            config_sample, repeat=2, timeout=5)
