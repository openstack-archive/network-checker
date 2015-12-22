#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

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
