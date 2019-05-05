Freebox Pymote
=============

Python library for the Freebox network-based input API (rudp, foil).
The documentation of the protocol is available here: http://dev.freebox.fr/sdk/

It aims to control Freebox Player devices.

This is a fork from the amazing work of Maxime Chéramy (remotefreebox)
The code is based from the C implementation available at https://github.com/fbx/ .

This fork allows usage for long running processes (servers):
- Uses asyncio
- Reconnects to Freebox player after a configurable timeout duration.
- Network errors proof
- Prevent any dead while loop
- Auto discovery is optional. Only manual configuration works across networks (ie: Docker network). Also, several Freebox player can be managed.

## Usage

Use the class FreeboxPymote, that automatically look for the network for a freebox.
Then, use the press method to simulate a key press.

    from freeboxpymote.freeboxpymote import FreeboxPymote

    fbx = FreeboxPymote(timeout=20)
    fbx.press("Chan+")
