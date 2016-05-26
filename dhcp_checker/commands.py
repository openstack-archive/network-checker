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
import logging

from cliff import command
from cliff import lister
from dhcp_checker import api
from dhcp_checker import utils


LOG = logging.getLogger(__name__)


class BaseCommand(command.Command):
    """Base command for all app"""
    def get_parser(self, prog_name):
        parser = super(BaseCommand, self).get_parser(prog_name)
        parser.add_argument('--timeout', default=5, type=int,
                            help="Provide timeout for each network request")
        parser.add_argument('--repeat', default=2, type=int,
                            help="Provide number of repeats for request")
        return parser


class ListDhcpServers(lister.Lister, BaseCommand):
    """Show list of dhcp servers on ethernet interfaces"""

    def get_parser(self, prog_name):
        parser = super(ListDhcpServers, self).get_parser(prog_name)
        parser.add_argument(
            '--ifaces', metavar='I', nargs='+',
            help='If no eth provided - will run against all except lo')
        return parser

    def take_action(self, parsed_args):
        LOG.info('Starting dhcp discover for {0}'.format(parsed_args.ifaces))
        res = list(api.check_dhcp(
            parsed_args.ifaces,
            timeout=parsed_args.timeout,
            repeat=parsed_args.repeat))
        # NOTE(dshulyak) unfortunately cliff doesnt allow to configure
        # PrettyTable output, see link:
        # https://github.com/dhellmann/cliff/blob/master/
        # cliff/formatters/table.py#L34
        # and in case i want always print empty table if nothing found
        # it is not possible by configuration
        if not res:
            res = [{}]
        return (utils.DHCP_OFFER_COLUMNS,
                [utils.get_item_properties(item, utils.DHCP_OFFER_COLUMNS)
                 for item in res])


class ListDhcpAssignment(lister.Lister, BaseCommand):
    """Make dhcp request to servers and receive acknowledgement messages"""

    def get_parser(self, prog_name):
        parser = super(ListDhcpAssignment, self).get_parser(prog_name)
        parser.add_argument('iface',
                            help='Ethernet interface name')
        parser.add_argument('endpoint',
                            help='Endpoint of server or multicast group')
        parser.add_argument('--range_start', dest='range_start',
                            help='Start of the range')
        parser.add_argument('--range_end', dest='range_end', default=None,
                            help='Start of the range')
        return parser

    def take_action(self, parsed_args):
        res = iter(api.check_dhcp_request(
            parsed_args.iface,
            parsed_args.endpoint,
            parsed_args.range_start,
            parsed_args.range_end, timeout=parsed_args.timeout))
        first = res.next()
        columns = first.keys()
        return columns, [first.values()] + [item.values() for item in res]


class DhcpWithVlansCheck(lister.Lister, BaseCommand):
    """Provide iface with list of vlans to check

    If no vlans created - they will be. After creation they won't be deleted.
    """

    def get_parser(self, prog_name):
        parser = super(DhcpWithVlansCheck, self).get_parser(prog_name)
        parser.add_argument('config',
                            help='Ethernet interface name')
        return parser

    def take_action(self, parsed_args):
        res = list(api.check_dhcp_with_vlans(json.loads(parsed_args.config),
                                             timeout=parsed_args.timeout,
                                             repeat=parsed_args.repeat))
        if not res:
            res = [{}]
            return (utils.DHCP_OFFER_COLUMNS,
                    [utils.get_item_properties(item, utils.DHCP_OFFER_COLUMNS)
                     for item in res])
