from shameleon_client.providers.base import ShameleonProvider


class ShameleonShell:
    """ Shell module for Shameleon.

    This module is a simple non-interactive shell that can be used to execute
    commands on the remote host.

    args:
        provider: ShameleonProvider instance to use for communication
    """

    def __init__(self, provider: ShameleonProvider) -> None:
        self._provider = provider

    def run(self):
        # Request a tunnel
        tunnel_id = self._provider.request_tunnel('sh')

        while True:
            entry = input('> ')
            self._provider.send_data(tunnel_id, entry.encode('utf-8'))
            while True:
                data = self._provider.receive_data(tunnel_id)
                if len(data) > 0:
                    print(data.decode('utf-8'))
                    break
