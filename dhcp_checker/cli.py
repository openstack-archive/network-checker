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

import logging
import os
import sys
# fixed in cmd2 >=0.6.6
os.environ['EDITOR'] = '/usr/bin/nano'

from cliff import commandmanager

from fuel_network_checker import base_app


class DhcpApp(base_app.BaseApp):
    DEFAULT_VERBOSE_LEVEL = 0
    LOG_FILENAME = '/var/log/dhcp_checker.log'

    def __init__(self):
        super(DhcpApp, self).__init__(
            description='Dhcp check application',
            version='0.1',
            command_manager=commandmanager.CommandManager('dhcp.check'),
        )

    def configure_logging(self):
        super(DhcpApp, self).configure_logging()

        # set scapy logger level only to ERROR
        # due to a lot of spam
        runtime_logger = logging.getLogger('scapy.runtime')
        runtime_logger.setLevel(logging.ERROR)


def main(argv=sys.argv[1:]):
    myapp = DhcpApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
