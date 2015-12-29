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
import os

import daemonize

LOG = logging.getLogger(__name__)


def run_server(server, config):
    daemon = daemonize.Daemonize(
        app=config['app'],
        pid=config['pidfile'],
        action=server.serve_forever,
        # keep open stdin, stdout, stderr and socket file
        keep_fds=[0, 1, 2, server.fileno()])
    try:
        daemon.start()
    # this is required to do some stuff after server is daemonized
    except SystemExit as e:
        if e.code is 0:
            return True
        raise


def cleanup(config):
    if os.path.exists(config['unix']):
        os.unlink(config['unix'])
    if os.path.exists(config['pidfile']):
        with open(config['pidfile'], 'r') as f:
            pid = f.read().strip('\n')
            try:
                os.kill(int(pid), 9)
            except OSError:
                # it is ok if proc already stopped
                pass
        os.unlink(config['pidfile'])
    return True
