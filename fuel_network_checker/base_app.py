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
from logging import handlers

from cliff.app import App


class BaseApp(App):
    DEFAULT_VERBOSE_LEVEL = 0
    LOG_FILENAME = ''  # This needs to be redefined in child class

    def configure_logging(self):
        super(BaseApp, self).configure_logging()
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s (%(module)s) %(message)s',
            "%Y-%m-%d %H:%M:%S")

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.ERROR)
        stream_handler.setFormatter(formatter)

        file_handler = handlers.TimedRotatingFileHandler(
            self.LOG_FILENAME)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
