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

import httplib
import SimpleXMLRPCServer
import socket
import xmlrpclib


class UnixStreamHTTPConnection(httplib.HTTPConnection):

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.host)

    def getreply(self):
        response = self.getresponse()
        self.file = response.fp
        return response.status, response.reason, response.msg

    def getfile(self):
        return self.file


class UnixStreamTransport(xmlrpclib.Transport, object):

    def __init__(self, socket_path):
        self.socket_path = socket_path
        super(UnixStreamTransport, self).__init__()

    def make_connection(self, host):
        return UnixStreamHTTPConnection(self.socket_path)


class UnixStreamHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):

    # if True leads to calling TCP_NODELAY on AF_UNIX socket
    # which results in Errno 95
    disable_nagle_algorithm = False


class UnixXMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):

    address_family = socket.AF_UNIX


def get_client(config):
    return xmlrpclib.Server(
        'http://arg_unused',
        transport=UnixStreamTransport(config['unix']))


def get_server(config):
    return UnixXMLRPCServer(
        config['unix'],
        requestHandler=UnixStreamHandler,
        logRequests=False)
