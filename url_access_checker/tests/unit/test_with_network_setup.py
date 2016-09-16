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

import unittest

import mock
import netifaces

from url_access_checker import cli
from url_access_checker import consts
from url_access_checker import errors
from url_access_checker import network


@mock.patch('url_access_checker.network.execute')
@mock.patch('url_access_checker.network.netifaces.gateways')
@mock.patch('requests.get', mock.Mock(status_code=200))
@mock.patch('url_access_checker.network.check_ready')
@mock.patch('url_access_checker.network.check_up')
@mock.patch('url_access_checker.network.check_exist')
@mock.patch('url_access_checker.network.check_ifaddress_present')
class TestVerificationWithNetworkSetup(unittest.TestCase):

    def assert_by_items(self, expected_items, received_items):
        """In case of failure will show difference only for failed item."""
        for expected, executed in zip(expected_items, received_items):
            self.assertEqual(expected, executed)

    def test_verification_route(self, mifaddr, mexist, mup, mready, mgat,
                                mexecute):
        mexecute.return_value = (0, '', '')
        mup.return_value = True
        mexist.return_value = True
        mifaddr.return_value = False
        mready.return_value = True

        default_gw, default_iface = '172.18.0.1', 'eth2'
        mgat.return_value = {
            'default': {netifaces.AF_INET: (default_gw, default_iface)}}

        iface = 'eth1'
        addr = '10.10.0.2/24'
        gw = '10.10.0.1'

        cmd = ['with', 'setup', '-i', iface,
               '-a', addr, '-g', gw, 'test.url']

        cli.main(cmd)

        execute_stack = [
            mock.call(['ip', 'a']),
            mock.call(['ip', 'ro']),
            mock.call(['ip', 'a', 'add', addr, 'dev', iface]),
            mock.call(['ip', 'ro', 'change', 'default', 'via', gw, 'dev', iface]),
            mock.call(['ip', 'a']),
            mock.call(['ip', 'ro']),
            mock.call(['ip', 'ro', 'change', 'default', 'via', default_gw,
                  'dev', default_iface]),
            mock.call(['ip', 'a', 'del', addr, 'dev', iface]),
            mock.call(['ip', 'a']),
            mock.call(['ip', 'ro'])]

        self.assert_by_items(mexecute.call_args_list, execute_stack)

    def test_verification_vlan(self, mifaddr, mexist, mup, mready, mgat,
                               mexecute):
        mexecute.return_value = (0, '', '')
        mup.return_value = False
        mexist.return_value = False
        mifaddr.return_value = False
        mready.return_value = True

        default_gw, default_iface = '172.18.0.1', 'eth2'
        mgat.return_value = {
            'default': {netifaces.AF_INET: (default_gw, default_iface)}}

        iface = 'eth1'
        addr = '10.10.0.2/24'
        gw = '10.10.0.1'
        vlan = '101'
        tagged_iface = '{0}.{1}'.format(iface, vlan)

        cmd = ['with', 'setup', '-i', iface,
               '-a', addr, '-g', gw, '--vlan', vlan, 'test.url']

        cli.main(cmd)

        execute_stack = [
            mock.call(['ip', 'a']),
            mock.call(['ip', 'ro']),
            mock.call(['ip', 'link', 'set', 'dev', iface, 'up']),
            mock.call(['ip', 'link', 'add', 'link', 'eth1', 'name',
                       tagged_iface, 'type', 'vlan', 'id', vlan]),
            mock.call(['ip', 'link', 'set', 'dev', tagged_iface, 'up']),
            mock.call(['ip', 'a', 'add', addr, 'dev', tagged_iface]),
            mock.call(['ip', 'ro', 'change', 'default',
                       'via', gw, 'dev', tagged_iface]),
            mock.call(['ip', 'a']),
            mock.call(['ip', 'ro']),
            mock.call(['ip', 'ro', 'change', 'default', 'via',
                       default_gw, 'dev', default_iface]),
            mock.call(['ip', 'a', 'del', addr, 'dev', tagged_iface]),
            mock.call(['ip', 'link', 'set', 'dev', tagged_iface, 'down']),
            mock.call(['ip', 'link', 'delete', tagged_iface]),
            mock.call(['ip', 'link', 'set', 'dev', iface, 'down']),
            mock.call(['ip', 'a']),
            mock.call(['ip', 'ro'])]

        self.assert_by_items(mexecute.call_args_list, execute_stack)


@mock.patch('url_access_checker.network.check_up')
class TestInterfaceSetup(unittest.TestCase):

    def assert_raises_message(self, exc_type, msg, func, *args, **kwargs):
        with self.assertRaises(exc_type) as e:
            func(*args, **kwargs)
        self.assertEqual(str(e.exception), msg)

    @mock.patch('url_access_checker.network.execute')
    def test_interface_ready(self, mexecute, mup):
        mexecute.return_value = (0, 'state UP', '')
        mup.return_value = True

        iface = 'eth1'
        consts.LINK_UP_TIMEOUT = 1

        self.assertTrue(network.check_ready(iface))

    @mock.patch('url_access_checker.network.check_ready')
    def test_negative_interface_down(self, mready, mup):
        mup.return_value = True
        mready.return_value = False

        iface = 'eth1'
        consts.LINK_UP_TIMEOUT = 1

        self.assert_raises_message(
            errors.CommandFailed,
            'Link protocol on interface %s isn\'t UP'.format(iface),
            lambda: network.Eth(iface).setup()
        )
