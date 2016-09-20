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

import socket
import struct

import pcap
import scapy.all as scapy


# it is not defined in every python version
SO_BINDTODEVICE = 25


class MulticastChecker(object):

    def __init__(self, group='225.0.0.250', port='13100',
                 uid='999', iface='eth0',
                 ttl=1, repeat=1, timeout=3):
        self.group = group
        self.port = int(port)
        self.ttl = ttl
        self.uid = uid
        self.repeat = repeat
        self.timeout = timeout
        self.receiver = None
        self.messages = []
        self.iface = iface

    def send(self):
        ttl_data = struct.pack('@i', self.ttl)
        _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,
                           ttl_data)
        _socket.setsockopt(
            socket.SOL_SOCKET,
            SO_BINDTODEVICE, self.iface)

        for _ in xrange(self.repeat):
            _socket.sendto(self.uid, (self.group, self.port))
        return {'group': self.group,
                'port': self.port,
                'iface': self.iface,
                'uid': self.uid}

    def listen(self):
        self._register_group()
        self._start_listeners()
        return {'group': self.group,
                'port': self.port,
                'iface': self.iface,
                'uid': self.uid}

    def _register_group(self):
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.receiver.setsockopt(
            socket.SOL_SOCKET,
            SO_BINDTODEVICE, self.iface)
        self.receiver.bind(('', self.port))
        group_packed = socket.inet_aton(self.group)
        group_data = struct.pack('4sL', group_packed, socket.INADDR_ANY)
        self.receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                                 group_data)

    def _start_listeners(self):
        self.listener = pcap.pcap(self.iface)
        udp_filter = 'udp and dst port {0}'.format(self.port)
        self.listener.setfilter(udp_filter)

    def get_info(self):
        for sock, pack in self.listener.readpkts():
            pack = scapy.Ether(pack)
            data, _ = pack[scapy.UDP].extract_padding(pack[scapy.UDP].load)
            self.messages.append(data.decode())
        self.receiver.close()
        return list(set(self.messages))

    def test(self):
        return {'test': 'test'}
