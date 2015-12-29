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

from url_access_checker import cli


class TestUrlCheckerCommands(unittest.TestCase):

    def setUp(self):
        self.urls = ['http://url{0}'.format(i) for i in range(10)]

    @mock.patch('requests.get')
    def test_check_urls_success(self, get_mock):
        cli.UrlAccessCheckApp.LOG_FILENAME = './url_access_checker.log'
        response_mock = mock.Mock()
        response_mock.status_code = 200
        get_mock.return_value = response_mock

        exit_code = cli.main(['check'] + self.urls)
        self.assertEqual(exit_code, 0)

    @mock.patch('url_access_checker.api.check_urls')
    def test_check_urls_proxies(self, check_mock):
        cli.UrlAccessCheckApp.LOG_FILENAME = './url_access_checker.log'
        proxies = {
            'http': 'http_proxy',
            'https': 'https_proxy'
        }
        cli.main(['check',
                  '--http-proxy', 'http_proxy',
                  '--https-proxy', 'https_proxy'] + self.urls)
        check_mock.assert_called_once_with(
            self.urls, proxies=proxies, timeout=60)

    @mock.patch('requests.get')
    def test_check_urls_fail(self, get_mock):
        response_mock = mock.Mock()
        response_mock.status_code = 404
        get_mock.return_value = response_mock

        exit_code = cli.main(['check'] + self.urls)
        self.assertEqual(exit_code, 1)

    def test_check_urls_fail_on_requests_error(self):
        exit_code = cli.main(['check'] + self.urls)
        self.assertEqual(exit_code, 1)
