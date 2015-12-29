#    Copyright 2014 Mirantis, Inc.
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

from stevedore import driver

from network_checker import config
from network_checker import daemon
from network_checker import xmlrpc


class Api(object):

    namespace = 'network_checker'

    def __init__(self, verification, **kwargs):
        self.verification = verification
        self.server_config = config.get_config()[verification]
        self.verification_config = dict(self.server_config['defaults'],
                                        **kwargs)

    def serve(self):
        daemon.cleanup(self.server_config)
        self.manager = driver.DriverManager(
            self.namespace,
            self.verification,
            invoke_on_load=True,
            invoke_kwds=self.verification_config)
        self.driver = self.manager.driver
        rpc_server = xmlrpc.get_server(self.server_config)
        # TODO(dshulyak) verification api should know what methods to serve
        rpc_server.register_function(self.driver.listen, 'listen')
        rpc_server.register_function(self.driver.send, 'send')
        rpc_server.register_function(self.driver.get_info, 'get_info')
        rpc_server.register_function(self.driver.test, 'test')
        return daemon.run_server(rpc_server, self.server_config)

    def listen(self):
        return xmlrpc.get_client(self.server_config).listen()

    def send(self):
        return xmlrpc.get_client(self.server_config).send()

    def info(self):
        return xmlrpc.get_client(self.server_config).get_info()

    def clean(self):
        return daemon.cleanup(self.server_config)

    def test(self):
        return xmlrpc.get_client(self.server_config).test()
