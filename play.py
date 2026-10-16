#!/usr/bin/env python3
"""Run an isolated Dark Souls III compatibility test with the installed bbport."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

from import_adapter import adapt_image


def make_test_app(root, data):
    """Give the isolated test its own Mac app identity for focus and input."""
    contents = data / 'DS3 Test.app' / 'Contents'
    binary = contents / 'MacOS' / 'bb-probe'
    binary.parent.mkdir(parents=True)
    shutil.copy2(root / 'bin/bb-probe', binary)
    (contents / 'lib').symlink_to(root / 'lib', target_is_directory=True)
    (binary.parent / 'gpu').symlink_to(root / 'bin/gpu', target_is_directory=True)
    (contents / 'Info.plist').write_bytes(plistlib.dumps({
        'CFBundleExecutable': 'bb-probe', 'CFBundleIdentifier': 'com.celayasolutions.ds3-test',
        'CFBundleName': 'DS3 Test', 'CFBundlePackageType': 'APPL', 'CFBundleVersion': '1',
        'NSHighResolutionCapable': True,
    }))
    # Sign only this copied app; never recurse through links to installed libraries.
    subprocess.run(['codesign', '--force', '--sign', '-', str(contents.parent)], check=True)
    return binary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--bbport', type=Path, default=Path.home() / 'Documents/bloodborne/runtime/engines/bbport-0.4-v1/bbport.app/Contents/Resources/bbport')
    parser.add_argument('--reference-game', type=Path, default=Path.home() / 'Documents/bloodborne/runtime/games/CUSA00900-109')
    parser.add_argument('--data', type=Path)
    parser.add_argument('--save-from', type=Path, help='Copy a prior test user folder into the fresh run')
    parser.add_argument('--timeout', type=int, default=120)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 600:
        parser.error('--timeout must be between 1 and 600 seconds')
    if subprocess.run(['pgrep', '-x', 'bb-probe'], stdout=subprocess.DEVNULL).returncode == 0:
        parser.error('Close the running bbport test or game first')
    game, root, reference = (p.expanduser().resolve() for p in (args.game, args.bbport, args.reference_game))
    for p in (game / 'eboot.bin', reference / 'eboot.bin', root / 'bin/bb-probe', root / 'scripts/link_modules.py'):
        if not p.is_file():
            parser.error(f'Missing input: {p}')
    sys.path.insert(0, str(root / 'scripts'))
    sys.dont_write_bytecode = True
    from prepare import sfo, prepare
    from game_check import image_sha256, SUPPORTED_IMAGE
    from link_modules import module, link
    info = sfo((game / 'sce_sys/param.sfo').read_bytes())
    if info.get('TITLE_ID') != 'CUSA03388' or info.get('APP_VER') != '01.00':
        parser.error('This experiment supports only DS3 CUSA03388 version 01.00')
    if image_sha256(reference) != SUPPORTED_IMAGE:
        parser.error('Reference executable does not match the installed Bloodborne contracts')
    data = (args.data or Path(__file__).parent / 'runtime' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')).expanduser().resolve()
    if data.exists():
        parser.error('Use a fresh --data folder to preserve previous tests')
    save_from = args.save_from.expanduser().resolve() if args.save_from else None
    if save_from and not (save_from / 'savedata/1/CUSA03388/DS30000').is_dir():
        parser.error('--save-from must be a DS3 test user folder containing DS30000')
    out = data / 'out'
    out.mkdir(parents=True)
    if save_from:
        shutil.copytree(save_from, data / 'user')
    else:
        (data / 'user').mkdir()
    (data / 'bbport.ini').write_text('show_fps=1\nupscaler=off\nobject_motion=0\n')
    binary = make_test_app(root, data)
    previous = os.environ.get('BB_SKIP_GAME_CHECK')
    os.environ['BB_SKIP_GAME_CHECK'] = '1'
    try:
        prepare(game, out)
    finally:
        if previous is None:
            os.environ.pop('BB_SKIP_GAME_CHECK', None)
        else:
            os.environ['BB_SKIP_GAME_CHECK'] = previous
    link(game, out)
    changes = adapt_image(out / 'boot-linked.bin', out / 'boot-ds3.bin',
                          module(game / 'eboot.bin'), module(reference / 'eboot.bin'))
    (out / 'import-adapter.json').write_text(json.dumps(changes, indent=2) + '\n')
    env = {key: value for key, value in os.environ.items() if not key.startswith('BB_')}
    env.update(BB_CONFIG=str(data / 'bbport.ini'), BB_FULLSCREEN='0', BB_OBJECT_MOTION='0',
               BB_VBLANK_HZ='60', BB_FRAME_STATS='1', BB_FRAME_LOG=str(out / 'frames.csv'),
               BB_VULKAN_LIBRARY=str(root / 'lib/libvulkan.1.dylib'),
               SDL_VULKAN_LIBRARY=str(root / 'lib/libvulkan.1.dylib'),
               VK_DRIVER_FILES=str(root / 'lib/kosmickrisp/kosmickrisp_mesa_icd.json'))
    subprocess.run([sys.executable, str(root / 'scripts/content_profile.py'), str(game), '--out', str(out)],
                   env=env, check=True)
    command = [str(binary), str(out / 'boot-ds3.bin'),
               '--content-profile', str(out / 'content.bin'), '--app0', str(game),
               '--user', str(data / 'user'), '--timeout', str(args.timeout)]
    report = {'title': info['TITLE'], 'title_id': info['TITLE_ID'], 'version': info['APP_VER'],
              'game': str(game), 'bbport': str(root), 'remapped_imports': len(changes),
              'timeout_seconds': args.timeout, 'gameplay_verified': False,
              'probe_sha256': hashlib.sha256((root / 'bin/bb-probe').read_bytes()).hexdigest()}
    print(f'Remapped {len(changes)} imports. Starting {args.timeout}-second test. Log: {out / "run.log"}', flush=True)
    with (out / 'run.log').open('w') as log:
        try:
            result = subprocess.run(command, env=env, cwd=root, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=args.timeout + 15)
            report['exit_code'] = result.returncode
        except subprocess.TimeoutExpired:
            report['exit_code'] = 124
            report['host_timeout'] = True
    log_text = (out / 'run.log').read_text(errors='replace')
    report['entered_game'] = 'Entering original x86-64 code' in log_text
    report['stops'] = [line for line in log_text.splitlines() if 'STOP:' in line or 'Guest fault' in line]
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)
    return report['exit_code'] if report['exit_code'] >= 0 else 128 - report['exit_code']


if __name__ == '__main__':
    raise SystemExit(main())
