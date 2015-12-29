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

import unittest2

import mock
import requests_mock

from url_access_checker import api
from url_access_checker import errors


class TestApi(unittest2.TestCase):

    def setUp(self):
        self.urls = ['http://url{0}'.format(i) for i in range(10)]
        self.paths = ['file:///tmp/test_api{0}'.format(i) for i in range(10)]
        self.ftps = ['ftp://url{0}'.format(i) for i in range(10)]

    @requests_mock.Mocker()
    def test_check_urls(self, req_mocker):
        for url in self.urls:
            req_mocker.get(url, status_code=200)

        check_result = api.check_urls(self.urls)

        self.assertTrue(check_result)

    @requests_mock.Mocker()
    def test_check_urls_fail(self, req_mocker):
        for url in self.urls:
            req_mocker.get(url, status_code=404)

        with self.assertRaises(errors.UrlNotAvailable):
            api.check_urls(self.urls)

    @mock.patch('os.path.exists')
    def test_check_paths(self, mock_exists):
        mock_exists.return_value = True
        check_result = api.check_urls(self.paths)

        self.assertTrue(check_result)

    @mock.patch('os.path.exists')
    def test_check_paths_fail(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(errors.UrlNotAvailable):
            api.check_urls(self.paths)

    @mock.patch('urllib2.urlopen')
    def test_check_ftp(self, _):
        check_result = api.check_urls(self.ftps, timeout=5)
        self.assertTrue(check_result)

    def test_check_ftp_fail(self):
        with self.assertRaises(errors.UrlNotAvailable):
            api.check_urls(self.paths)
