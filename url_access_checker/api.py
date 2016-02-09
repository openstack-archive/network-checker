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

import json
import os
import socket

import requests
import six
from six.moves import urllib

from url_access_checker import errors


def check_urls(urls, proxies=None, timeout=60):
    """Checks a set of urls to see if they are valid

    Url is valid if
    - it returns 200 upon requesting it with http (if it doesn't specify
    protocol as "file")
    - it is an existing file or directory (if the protocol used in url is
    "file")

    Arguments:
    urls -- an iterable containing urls for testing
    proxies -- proxy servers to use for the request
    timeout -- the max time to wait for a response, default 60 seconds
    """
    responses = {u: _unavailable_url(u, proxies=proxies, timeout=timeout)
                 for u in urls}

    failed_responses = {k: v for k, v in six.iteritems(responses) if v}

    if failed_responses:
        raise errors.UrlNotAvailable(json.dumps(
            {'failed_urls': failed_responses.keys()}))
    else:
        return True


def _unavailable_url(url, proxies=None, timeout=60):
    """Return the result of url test

    Arguments:
    url -- a string containing url for testing, can be local file
    proxies -- proxy servers to use for the request
    timeout -- the max time to wait for a response, default 60 seconds

    Result content:
        result -- boolean value, True if the url is deemed failed
    """

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == 'file':
        return _get_file_existence(url)
    elif parsed.scheme in ['http', 'https']:
        return _get_http_response(url, proxies, timeout)
    elif parsed.scheme == 'ftp':
        return _get_ftp_response(url, timeout)
    else:
        raise errors.InvalidProtocol(url)


def _get_file_existence(url):
    path = url[len('file://'):]
    return not os.path.exists(path)


def _get_http_response(url, proxies=None, timeout=60):
    try:
        # requests seems to correctly handle various corner cases:
        # proxies=None or proxies={} mean 'use the default' rather than
        # "don't use proxy". To force a direct connection one should pass
        # proxies={'http': None}.
        # Setting the timeout for requests.get(...) sets max request time. We
        # want to set a value to prevent this process from hanging as the
        # default timeout is None which can lead to bad things when processes
        # never exit. LP#1478138
        response = requests.get(url, proxies=proxies, timeout=timeout)
        return response.status_code != 200
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
            requests.exceptions.ProxyError,
            ValueError,
            socket.timeout):
        return True


def _get_ftp_response(url, timeout=60):
    """Return the result of ftp url test

    It will try to open ftp url as anonymous user and return True if
    any errors occur, or return False otherwise.
    """
    try:
        # NOTE(mkwiek): requests don't have tested ftp adapter yet, so
        # lower level urllib2 is used here
        urllib.request.urlopen(url, timeout=timeout)
        return False
    except urllib.error.URLError:
        return True
