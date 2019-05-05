from . import address
from . import endpoint
from . import peer
from . import packet
import logging

_LOGGER = logging.getLogger(__name__)

class client_handler(object):
    def __init__(self, handle_packet = None, link_info = None, connected = None, server_lost = None):
        self.handle_packet = handle_packet or self.default_handle_packet
        self.link_info = link_info or self.default_link_info
        self.connected = connected or self.default_connected
        self.server_lost = server_lost or self.default_server_lost

    @staticmethod
    def default_handle_packet(cl, cmd, data):
        pass

    @staticmethod
    def default_link_info(cl, info_):
        pass

    @staticmethod
    def default_connected(cl):
        pass

    @staticmethod
    def default_server_lost(cl):
        pass

class client(object):
    def __init__(self, rudp, handler):
        self.rudp = rudp
        self.handler = handler
        self.address = address.address()
        self.endpoint = endpoint.endpoint(
            rudp, endpoint.endpoint_handler(self.handle_endpoint_packet))
        self.connected = False
        self.peer = None
        self.peer_handler = peer.peer_handler(self.handle_data_packet,
                                              self.link_info, self.peer_dropped)

    def link_info(self, peer, info):
        pass

    def handle_endpoint_packet(self, addr, pc):
        self.peer.incoming_packet(pc)
        if not self.connected:
            self.connected = True
            self.handler.connected(self)

    def peer_dropped(self, peer):
        _LOGGER.warning("client peer dropped")

    def handle_data_packet(self, peer, pc):
        command = pc.header.command
        self.handler.handle_packet(self, command, pc.data)

    def connect(self):
        addr = self.address.get()
        self.peer = peer.peer(self.rudp, addr, self.peer_handler, self.endpoint)
        self.endpoint.set_addr(('', 0))
        self.peer.send_connect()
        self.endpoint.bind()

    def close(self):
        self.endpoint.close()

    def deinit(self):
        pass

    def set_hostname(self, hostname, port, ip_flags):
        self.address.set_hostname(hostname, port, ip_flags)

    def set_addr(self, addr):
        self.address.set(addr)

    def send(self, reliable, command, data):
        if command + packet.RUDP_CMD_APP > 255:
            return None
        if not self.connected:
            return None

        pc = packet.packet_data()
        pc.header.command = packet.RUDP_CMD_APP + command
        pc.data = data

        if reliable:
            self.peer.send_reliable(pc)
        else:
            self.peer.send_unreliable(pc)
