from __future__ import annotations

import yaml

from shameleon_client.providers.base import ShameleonProvider


class Profile:
    # DOC
    def __init__(self, name: str, provider: str, description: str = ''):
        self.name = name
        self._provider: ShameleonProvider | None = None
        self._provider_name = provider
        self.description = description
        # Backdoor config
        self.backdoor_secret: str = ''
        self.packet_size: int = 0

    @classmethod
    def load(cls, file_path: str) -> Profile:
        with open(file_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        profile = cls(
            name=data['general']['name'],
            provider=data['general']['provider'],
            description=data['general']['description'],
        )
        profile.backdoor_secret = data['backdoor']['secret']
        profile.packet_size = data['backdoor']['packet_size']
        return profile

    @property
    def provider(self) -> ShameleonProvider:
        if self._provider is None:
            self._provider = ShameleonProvider.get_module_from_name(self._provider_name)(self.backdoor_secret)
            self._provider.configure(self.packet_size)
        return self._provider
