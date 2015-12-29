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

import os
import sys
# fixed in cmd2 >=0.6.6
os.environ['EDITOR'] = '/usr/bin/nano'

from cliff.commandmanager import CommandManager

from fuel_network_checker import base_app


class UrlAccessCheckApp(base_app.BaseApp):
    LOG_FILENAME = '/var/log/url_access_checker.log'

    def __init__(self):
        super(UrlAccessCheckApp, self).__init__(
            description='Url access check application',
            version='0.1',
            command_manager=CommandManager('urlaccesscheck'),
        )


def main(argv=sys.argv[1:]):
    myapp = UrlAccessCheckApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
