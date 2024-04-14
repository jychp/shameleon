import asyncio
import socket

from shameleon_client.features.lforward import lfoward_connection_hook
from shameleon_client.providers.base import ShameleonProvider


class LocalServer:
    # DOC
    def __init__(self, port: int, module: str, provider: ShameleonProvider, **kwargs) -> None:
        self._port = port
        self._module = module
        self._host = 'localhost'
        self._provider = provider
        self._config = kwargs

    async def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self._host, self._port))
        server.listen(1)
        server.setblocking(False)

        loop = asyncio.get_event_loop()

        while True:  # TODO: Add a way to stop the server
            client, _ = await loop.sock_accept(server)
            tunnel_id = await self._provider.request_tunnel(self._module)
            # Hook for lforward
            if self._module == 'lf':
                remote_host = self._config.get('remote_host')
                remote_port = self._config.get('remote_port')
                if not await lfoward_connection_hook(remote_host, remote_port, tunnel_id, self._provider):
                    print(f'[-] Connection to {remote_host}:{remote_port} failed')
                    client.close()
                    break
            loop.create_task(self.handle_input(client, tunnel_id))
            loop.create_task(self.handle_output(client, tunnel_id))

    async def handle_input(self, client, tunnel_id):
        loop = asyncio.get_event_loop()
        while True:  # TODO: Add a way to stop the server
            data = await loop.sock_recv(client, 1024)
            if len(data) == 0:
                await asyncio.sleep(0.1)
                continue
            self._provider.send_data(tunnel_id, data)

    async def handle_output(self, client, tunnel_id):
        loop = asyncio.get_event_loop()
        while True:  # TODO: Add a way to stop the server
            data = self._provider.receive_data(tunnel_id)
            if len(data) == 0:
                await asyncio.sleep(0.1)
                continue
            await loop.sock_sendall(client, data)
