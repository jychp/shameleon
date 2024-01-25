#!/bin/env python3
import argparse

from shameleon_client.modules.shell import ShameleonShell
from shameleon_client.providers.dummy import DummyProvider


def main():
    # ARGS PARSING
    parser = argparse.ArgumentParser("Shameleon client - v0.1")
    parser.add_argument(
        'module',
        type=str,
        choices=['shell', 'socks'],
        help='Names of module to run',
    )
    # TODO: Add backdoor selection
    args = parser.parse_args()

    # TODO: Load with backdoor profile
    provider = DummyProvider()
    provider.start()

    if args.module == 'shell':
        shell = ShameleonShell(provider)
        shell.run()
    elif args.module == 'socks':
        raise NotImplementedError('SOCKS module not implemented yet ;)')


if __name__ == '__main__':
    main()
