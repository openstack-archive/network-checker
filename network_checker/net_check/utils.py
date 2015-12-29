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

from contextlib import contextmanager
from functools import partial
import logging
import signal


log = logging.getLogger(__name__)


class TimeoutException(KeyboardInterrupt):
    """Exception should be raised if timeout is exceeded."""


def timeout_handler(timeout, signum, frame):
    raise TimeoutException("Timeout {0} seconds exceeded".format(timeout))


@contextmanager
def signal_timeout(timeout, raise_exc=True):
    """Timeout handling using signals

    :param timeout: timeout in seconds, integer
    :param raise_exc: bool to control suppressing of exception
    """
    handler = partial(timeout_handler, timeout)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)

    try:
        yield
    except TimeoutException as exc:
        if raise_exc:
            raise
        else:
            log.warning(str(exc))
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
