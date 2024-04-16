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
        # Client config
        self.http_timeout: int = 0
        self.shell_enabled: bool = False
        self.shell_port: int = 7777
        self.socks_enabled: bool = False
        self.socks_port: int = 1080
        self.lforward_enabled: bool = False
        self.lforward: dict = {}
        # Backdoor config
        self.backdoor_secret: str = ''
        self.backdoor_custom: dict[str, Any] = {}
        self.packet_size: int = 0
        self.packet_number: int = 0
        self.backdoor_timeout: int = 0
        self.backdoor_min_delay: int = 0
        self.backdoor_factor_delay: float = 0.0
        self.backdoor_max_delay: int = 0

    @classmethod
    def load(cls, file_path: str) -> Profile:
        """ Load profile from file

        This method is used to load a profile from a YAML file.

        Args:
            file_path (str): path to the profile file

        Returns:
            Profile: profile loaded from the file
        """
        with open(file_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        profile = cls(
            name=data['general']['name'],
            provider=data['general']['provider'],
            description=data['general']['description'],
        )
        profile.http_timeout = data['client']['http_timeout']
        profile.shell_enabled = data['client'].get('shell', {}).get('enabled', False)
        profile.shell_port = data['client'].get('shell', {}).get('port', 7777)
        profile.socks_enabled = data['client'].get('socks', {}).get('enabled', False)
        profile.socks_port = data['client'].get('socks', {}).get('port', 8888)
        profile.lforward_enabled = data['client'].get('lforward', {}).get('enabled', False)
        for rule in data['client'].get('lforward', {}).get('rules', []):
            profile.lforward[rule['local_port']] = {
                'remote_host': rule.get('remote_host', 'localhost'),
                'remote_port': rule.get('remote_port', 3306),
            }
        profile.backdoor_secret = data['backdoor']['secret']
        profile.packet_size = data['backdoor']['packet_size']
        profile.packet_number = data['backdoor']['packet_number']
        profile.backdoor_timeout = data['backdoor']['timeout']
        profile.backdoor_custom = data['backdoor'].get('custom', {})
        profile.backdoor_min_delay = data['backdoor'].get('min_delay', 1000)
        profile.backdoor_factor_delay = data['backdoor'].get('factor_delay', 0.5)
        profile.backdoor_max_delay = data['backdoor'].get('max_delay', 10000)
        return profile

    def serialize_for_backdoor(self) -> str:
        """ Serialize profile for backdoor """
        payload = {
            "secret": self.backdoor_secret,
            "packet_size": self.packet_size,
            "packet_number": self.packet_number,
            "timeout": self.backdoor_timeout,
            "custom": self.backdoor_custom,
            "min_delay": self.backdoor_min_delay,
            "factor_delay": self.backdoor_factor_delay,
            "max_delay": self.backdoor_max_delay,
        }
        return json.dumps(payload)
