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

import logging
import sys

from cliff import command

import url_access_checker.api as api
import url_access_checker.errors as errors
from url_access_checker.network import manage_network


LOG = logging.getLogger(__name__)


class CheckUrls(command.Command):
    """Check if it is possible to retrieve urls."""
    def get_parser(self, prog_name):
        parser = super(CheckUrls, self).get_parser(prog_name)
        parser.add_argument('urls', type=str, nargs='+',
                            help='List of urls to check')
        parser.add_argument('--timeout', type=int, default=60,
                            help='Max time to wait for response, Default: 60')
        parser.add_argument('--http-proxy', type=str, default=None,
                            help='Http proxy, Default: None')
        parser.add_argument('--https-proxy', type=str, default=None,
                            help='Https proxy, Default: None')
        return parser

    def take_action(self, parsed_args):
        LOG.info('Starting url access check for {0}'.format(parsed_args.urls))
        proxies = {}
        if parsed_args.http_proxy:
            proxies['http'] = parsed_args.http_proxy
        if parsed_args.https_proxy:
            proxies['https'] = parsed_args.https_proxy
        try:
            api.check_urls(parsed_args.urls,
                           proxies=proxies or None,
                           timeout=parsed_args.timeout)
        except errors.UrlNotAvailable as e:
            sys.stdout.write(str(e))
            raise e


class CheckUrlsWithSetup(CheckUrls):

    def get_parser(self, prog_name):
        parser = super(CheckUrlsWithSetup, self).get_parser(
            prog_name)
        parser.add_argument('-i', type=str, help='Interface', required=True)
        parser.add_argument('-a', type=str, help='Addr/Mask pair',
                            required=True)
        parser.add_argument('-g', type=str, required=True,
                            help='Gateway to be used as default')
        parser.add_argument('--vlan', type=int, help='Vlan tag')
        return parser

    def take_action(self, pa):
        with manage_network(pa.i, pa.a, pa.g, pa.vlan):
            return super(
                CheckUrlsWithSetup, self).take_action(pa)
