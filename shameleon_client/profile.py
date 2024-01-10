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

    @classmethod
    def load(cls, file_path: str) -> Profile:
        with open(file_path) as f:
            data = yaml.safe_load(f)
        profile = cls(
            name=data['general']['name'],
            provider=data['general']['provider'],
            description=data['general']['description'],
        )
        return profile

    @property
    def provider(self) -> ShameleonProvider:
        if self._provider is None:
            self._provider = ShameleonProvider.get_module_from_name(self._provider_name)()
        return self._provider
