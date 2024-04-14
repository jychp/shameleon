import socket
import time

from shameleon_client.providers.base import ShameleonProvider


class ShameleonLforward:
    # DOC

    def __init__(self, provider: ShameleonProvider, parameters: str) -> None:
        self._port, self._remote_host, self._remote_port = parameters.split(':', 2)
        self._provider = provider
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host = 'localhost'

    def run(self):
        # Request a tunnel
        tunnel_id = self._provider.request_tunnel('lf')

        # Start the listener
        server_address = (self._host, int(self._port))
        print('[i] Starting listener on {} port {}'.format(*server_address))
        self._socket.bind(server_address)
        self._socket.listen(1)

        print('[i] Waiting for a connection ...')
        connection, client_address = self._socket.accept()
        connection.setblocking(False)

        print('[+] Connection from', client_address)

        # Send connection command
        payload = self._remote_host + '!' + str(self._remote_port)
        self._provider.send_data(tunnel_id, payload.encode('utf-8'))
        while True:
            data = self._provider.receive_data(tunnel_id)
            if len(data) > 0:
                if data.decode('utf-8') != 'OK':
                    print('[-] Connection failed')
                    return
                else:
                    break
            time.sleep(0.1)

        while True:
            # GET data from provider and send it to socket
            data = self._provider.receive_data(tunnel_id)
            if len(data) > 0:
                connection.sendall(data)
            # GET data from socket and send it to provider
            try:
                data = connection.recv(1024)  # TODO: Set size from config
                if len(data) > 0:
                    self._provider.send_data(tunnel_id, data)
            except BlockingIOError:
                pass
            time.sleep(0.1)
