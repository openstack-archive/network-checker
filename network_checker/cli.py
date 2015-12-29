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

"""Fuel network checker
Available verifications: multicast

Example:
  fuel-netcheck multicast serve listen send info clean

Multicast config options:
  group: 225.0.0.250
  port: 13310
  ttl: 5
  uid: '1001'
  repeat: 3
  iface: eth0
  timeout: 10

"""

import argparse
import json
import textwrap

from network_checker import api


def parse_args():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'verification',
        help="Type of verification that should be started.")
    parser.add_argument(
        'actions', nargs='+',
        help="List of actions to perform.")
    # TODO(dshulyak) Add posibility to provide args like regular shell args
    parser.add_argument(
        '-c', '--config', default='{}',
        help="User defined configuration in json format.")
    return parser.parse_args()


def main():
    args = parse_args()
    user_data = json.loads(args.config)
    api_instance = api.Api(args.verification, **user_data)
    # Print only last response if user requires multiple sequantial actions
    for action in args.actions:
        result = getattr(api_instance, action)()
    print(json.dumps(result))
