import asyncio

from shameleon_client.providers.base import ShameleonProvider


async def lfoward_connection_hook(remote_host: str, remote_port: int, tunnel_id: str, provider: ShameleonProvider):
    # DOC
    payload = remote_host + '!' + str(remote_port)
    provider.send_data(tunnel_id, payload.encode('utf-8'))
    while True:
        data = provider.receive_data(tunnel_id)
        if len(data) > 0:
            if data.decode('utf-8') != 'OK':
                print('[-] Connection failed')
                return False
            else:
                return True
        await asyncio.sleep(0.1)
