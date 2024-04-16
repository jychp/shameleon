import asyncio
import socket

from shameleon_client.features.lforward import lfoward_connection_hook
from shameleon_client.features.socks import socks_connection_hook
from shameleon_client.providers.base import ShameleonProvider


class LocalServer:
    """ Local server to expose a service of the backdoor.

    This class is used to expose a service of the backdoor on a local port.
    It is used to create a local server that will be used to communicate with
    the backdoor.
    """

    def __init__(self, port: int, module: str, provider: ShameleonProvider, **kwargs) -> None:
        self._port = port
        self._module = module
        self._host = 'localhost'
        self._provider = provider
        self._config = kwargs
        self._handlers: list[asyncio.Task] = []
        self._clients: list[socket.socket] = []

    async def run(self) -> None:
        """ Run the local server.

        This method is used to run the local server. It will listen on the
        specified port and handle incoming connections.
        Each connection will be handled by a separate asyncio task.
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self._host, self._port))
        server.listen(1)
        server.setblocking(False)

        loop = asyncio.get_event_loop()

        try:
            while True:
                client, _ = await loop.sock_accept(server)
                tunnel_id = await self._provider.request_tunnel(self._module)
                # Hook for SOCKS
                if self._module == 'sx':
                    if not await socks_connection_hook(client, tunnel_id, self._provider):
                        print('[!] SOCKS connection failed')
                        break
                # Hook for lforward
                if self._module == 'lf':
                    remote_host = str(self._config.get('remote_host'))
                    remote_port = int(self._config.get('remote_port', 0))
                    if not await lfoward_connection_hook(remote_host, remote_port, tunnel_id, self._provider):
                        print(f'[!] Connection to {remote_host}:{remote_port} failed')
                        break
                self._handlers.append(loop.create_task(self._handle_input(client, tunnel_id)))
                self._handlers.append(loop.create_task(self._handle_output(client, tunnel_id)))
                self._clients.append(client)
        except asyncio.CancelledError:
            pass

        if len(self._handlers) > 0:
            print(f'[.] Stoping handlers for {self._module} on port {self._port}')
            for handler in self._handlers:
                handler.cancel()
        if len(self._clients) > 0:
            print(f'[.] Closing clients for {self._module} on port {self._port}')
            for client in self._clients:
                client.close()
        print(f'[.] Closing server for {self._module} on port {self._port}')
        server.shutdown(socket.SHUT_RDWR)
        server.close()

    async def _handle_input(self, client: socket.socket, tunnel_id: str) -> None:
        try:
            loop = asyncio.get_event_loop()
            while True:
                data = await loop.sock_recv(client, 1024)
                if len(data) == 0:
                    await asyncio.sleep(0.1)
                    continue
                self._provider.send_data(tunnel_id, data)
        except asyncio.CancelledError:
            return

    async def _handle_output(self, client: socket.socket, tunnel_id: str) -> None:
        try:
            loop = asyncio.get_event_loop()
            while True:
                data = self._provider.receive_data(tunnel_id)
                if len(data) == 0:
                    await asyncio.sleep(0.1)
                    continue
                await loop.sock_sendall(client, data)
        except asyncio.CancelledError:
            return
