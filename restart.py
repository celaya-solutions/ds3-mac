#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 CSR (Celaya Solutions)
"""Reopen a prepared DS3 session, backing up its saves before each launch."""
import argparse
from datetime import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from play import TUNED, parse_env, runtime_environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path, help='Completed play.py session folder')
    parser.add_argument('--fps-size', type=int, choices=range(1, 7), default=1,
                        help='Counter scale; above 1 requires the optional overlay patch')
    parser.add_argument('--tuned', action='store_true',
                        help='Apply the measured October 21 runtime setup instead of the recorded one')
    parser.add_argument('--env', action='append', default=[], metavar='KEY=VALUE',
                        help='Runtime (BB_*) or shader cache (MESA_*) override; replaces the recorded ones')
    args = parser.parse_args()
    data = args.data.expanduser().resolve()
    try:
        extras = [*(TUNED if args.tuned else ()), *parse_env(args.env)]
        report = json.loads((data / 'out/result.json').read_text())
        if not args.tuned and not args.env:
            extras = list(report.get('extra_env', []))
        if (report['title_id'], report['version']) != ('CUSA03388', '01.00'):
            parser.error('This launcher supports only DS3 CUSA03388 version 01.00')
        game, root = Path(report['game']), Path(report['bbport'])
        if report['runtime_layout'] not in ('source', 'packaged'):
            parser.error('Unknown runtime layout')
        if args.fps_size > 1 and report['runtime_layout'] != 'source':
            parser.error('--fps-size above 1 needs the source runtime with the optional overlay patch')
        if 'app_probe_sha256' not in report:
            parser.error('Older session report; prepare a fresh session with play.py --save-from first')
        contents = data / 'DS3 Test.app/Contents'
        binary = contents / 'MacOS/bb-probe'
        libraries = (contents / 'lib').resolve()
        gpu = contents / 'MacOS/gpu/libbbgpu.dylib'
        for path in (binary, gpu, data / 'out/boot-ds3.bin', data / 'out/content.bin',
                     data / 'bbport.ini', game / 'eboot.bin',
                     libraries / 'libvulkan.1.dylib',
                     libraries / 'kosmickrisp/kosmickrisp_mesa_icd.json'):
            if not path.is_file():
                parser.error(f'Missing input: {path}')
        if not root.is_dir() or not (data / 'user/savedata/1/CUSA03388/DS30000').is_dir():
            parser.error('Missing runtime directory or DS3 save; prepare a session with play.py first')
        for path, key in ((binary, 'app_probe_sha256'), (gpu, 'gpu_sha256')):
            if hashlib.sha256(path.read_bytes()).hexdigest() != report[key]:
                parser.error('Runtime changed; prepare a fresh session with play.py --save-from first')
        patches = data / 'out/patches.bin' if 'patches_sha256' in report else None
        if patches and (not patches.is_file()
                        or hashlib.sha256(patches.read_bytes()).hexdigest() != report['patches_sha256']):
            parser.error('Patch file changed; prepare a fresh session with play.py --save-from first')
        with (data / '.play.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                parser.error('This DS3 session is already running')
            if subprocess.run(['pgrep', '-x', 'bb-probe'], stdout=subprocess.DEVNULL).returncode == 0:
                parser.error('Close the running bbport test or game first')
            stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
            backup = data / 'backups' / stamp
            shutil.copytree(data / 'user', backup / 'user')
            shutil.copy2(data / 'bbport.ini', backup / 'bbport.ini')
            log_path = data / 'out' / f'play-{stamp}.log'
            print(f'Save backup: {backup}\nLog: {log_path}\nQuit through the game menu.', flush=True)
            command = [str(binary), str(data / 'out/boot-ds3.bin'),
                       '--content-profile', str(data / 'out/content.bin'), '--app0', str(game),
                       '--user', str(data / 'user'),
                       *(['--patches', str(patches)] if patches else []), '--timeout', '0']
            with log_path.open('x') as log:
                result = subprocess.run(command, cwd=root,
                                        env=runtime_environment(data, libraries, args.fps_size, extra=extras),
                                        stdout=log, stderr=subprocess.STDOUT)
            print(f'Game exited with code {result.returncode}. Log: {log_path}', flush=True)
            return result.returncode if result.returncode >= 0 else 128 - result.returncode
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
