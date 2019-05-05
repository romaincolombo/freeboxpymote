from zeroconf import ServiceBrowser, Zeroconf
import socket
import time
import asyncio

# Author: 1337Woflpack.

servers = []


class Server(object):
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name


class MyListener(object):
    # def addService(self, zeroconf, type, name):
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            servers.append(Server(socket.inet_ntoa(info.address),
                                  info.port, info.server))

async def detect(timeout=None, first=False):
    global servers
    zeroconf = Zeroconf()
    listener = MyListener()
    ServiceBrowser(zeroconf, "_hid._udp.local.", listener=listener)
    freeboxes = []
    finished = False
    if not timeout:
        timeout = 10
    timeout_time = time.time() + timeout
    while not finished and time.time() < timeout_time:
        for server in servers:
            if 'Freebox' in server.name and server not in freeboxes:
                freeboxes.append(server)
                if first:
                    finished = True
        await asyncio.sleep(0.1)
    zeroconf.close()
    servers = []
    return freeboxes

async def detect_first(timeout=None):
    freeboxes = await detect(timeout=timeout, first=True)
    if not freeboxes:
        return None
    return freeboxes[0]
