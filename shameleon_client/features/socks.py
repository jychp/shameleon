import asyncio
import socket
from struct import unpack

from shameleon_client.providers.base import ShameleonProvider

# Constants
VERSION = b'\x05'
M_NOAUTH = b'\x00'
M_NOTAVAILABLE = b'\xff'
CMD_CONNECT = b'\x01'
ATYP_IPV4 = b'\x01'
ATYP_DOMAINNAME = b'\x03'


async def socks_connection_hook(client: socket.socket, tunnel_id: str, provider: ShameleonProvider):
    # DOC
    loop = asyncio.get_event_loop()
    # Identification
    while True:  # TODO: Add timeout
        identification_packet = await loop.sock_recv(client, 1024)
        if len(identification_packet) == 0:
            await asyncio.sleep(0.1)
        else:
            break
    resp = _handle_identification(identification_packet)
    if resp is None:
        await loop.sock_sendall(client, VERSION + M_NOTAVAILABLE)
        return False
    await loop.sock_sendall(client, VERSION + resp)
    # Connection request
    while True:  # TODO: Add timeout
        request_packet = await loop.sock_recv(client, 1024)
        if len(request_packet) == 0:
            await asyncio.sleep(0.1)
        else:
            break
    dst = _handle_request(request_packet)
    if dst is None:
        return False
    payload = dst[0].decode('utf-8') + '!' + str(dst[1])
    provider.send_data(tunnel_id, payload.encode('utf-8'))
    while True:  # TODO: Add timeout
        data = provider.receive_data(tunnel_id)
        if len(data) > 0:
            if data.decode('utf-8') != 'OK':
                await loop.sock_sendall(client, VERSION + b'\x01\x00\x00\x00\x00\x00\x00')
                return False
            else:
                await loop.sock_sendall(client, VERSION + b'\x00\x00' + ATYP_IPV4 + b'\x00\x00\x00\x00' + b'\x00\x00')
                return True
        await asyncio.sleep(0.1)


def _handle_identification(data: bytes) -> bytes | None:
    version = data[0:1]
    nmethods = data[1]
    methods = data[2:]
    if version != VERSION:
        print(f'[!] Socks version {version} not supported')
        return None
    if len(methods) != nmethods:
        print('[!] Socks methods mismatch')
        return None
    for method in methods:
        if method == ord(M_NOAUTH):
            return M_NOAUTH
    print('[!] Socks: No supported method')
    return None


def _handle_request(data: bytes) -> tuple[bytes, int] | None:
    version = data[0:1]
    cmd = data[1:2]
    rsv = data[2:3]
    atyp = data[3:4]
    if version != VERSION:
        print(f'[!] Socks version {version} not supported')
        return None
    if cmd != CMD_CONNECT:
        print(f'[!] Socks command {cmd} not supported')
        return None
    if rsv != b'\x00':
        print(f'[!] Socks reserved {rsv} not supported')
        return None
    # IPV4
    if atyp == ATYP_IPV4:
        return (
            socket.inet_ntoa(data[4:-2]).encode('utf-8'),
            int(unpack('>H', data[8:len(data)])[0]),
        )
    # DOMAIN NAME
    elif atyp == ATYP_DOMAINNAME:
        sz_domain_name = data[4]
        dst_addr = data[5: 5 + sz_domain_name - len(data)]
        port_to_unpack = data[5 + sz_domain_name:len(data)]
        dst_port = unpack('>H', port_to_unpack)[0]
        return (dst_addr, dst_port)
    return None
