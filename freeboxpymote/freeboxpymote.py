#/usr/bin/python3

import sys
import asyncio
from threading import Thread

from .detectserver import detect
from .rudp.client import client_handler
from .event_loop import event_loop
from .rudp.rudp import rudp
from .rudp_hid_client import rudp_hid_client
from .fbx_descriptor import fbx_foils_hid_device_descriptor, fbx_get_command


def info(s):
    print(s, file=sys.stderr)

def success(s):
    print(s, file=sys.stderr)


class FreeboxPymote(object):
    def __init__(self, host = None, port = None, timeout = 0):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._loop_thread = None
        self._client = None

    async def _detect(self):
        if not self._host or not self._port:
            # find freebox player
            freebox = await detect()
            if not freebox:
                raise Exception("Freebox player not found.")
            success("%s found at %s:%s" % (freebox.name, freebox.address, freebox.port))
            self._host = freebox.address
            self._port = freebox.port

    def _reset_client(self):
        if self._client:
            try:
                self._client.base.endpoint.socket.close()
            except Exception as e:
                info("Socket closing failure. %s" % e)
            finally:
                self._client = None

    def _is_loop_thread_awake(self):
        if not self._loop_thread:
            return False
        return self._loop_thread.is_alive()

    async def _connect(self):
        await self._detect()

        if not self._is_loop_thread_awake():
            self._reset_client()

            # rudp event loop
            self._evtloop = event_loop(self._timeout)
            r = rudp(self._evtloop)
            self._loop_thread = Thread(target=r.evtloop.loop)
            self._loop_thread.daemon = True
            self._loop_thread.start()

        if not self._client:
            try:
                self._client = rudp_hid_client(r, client_handler(), (self._host, self._port))
                await self._client.setup_device(fbx_foils_hid_device_descriptor)
            except Exception as e:
                self._reset_client
                raise e

        self._evtloop.wake_up()

    async def press_async(self, key):
        info("pressing %s" % key)
        await self._connect()
        self._client.send_command(*fbx_get_command(key))

    async def write_async(self, text):
        await self._connect()
        for l in text:
            self._client.send_command(1, ord(l))

    def press(self, key):
        asyncio.get_event_loop().run_until_complete(self.press_async(key))

    def write(self, text):
        asyncio.get_event_loop().run_until_complete(self.write_async(text))
