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

from logging import getLogger
import subprocess

logger = getLogger(__name__)


def execute(cmd):
    logger.debug('Executing command %s', cmd)
    command = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = command.communicate()
    msg = 'Command {0} executed. RC {1}, stdout {2}, stderr {3}'.format(
        cmd, command.returncode, stdout, stderr)
    if command.returncode:
        logger.error(msg)
    else:
        logger.debug(msg)
    return command.returncode, stdout, stderr
