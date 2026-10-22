#!/usr/bin/env python3
"""Run an isolated Dark Souls III compatibility test with the installed bbport."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys

from import_adapter import adapt_image


DEFAULT_SETTINGS = ('show_fps=1\nupscaler=metalfx\npreset=0\nobject_motion=0\n'
                    'output_res=1920x1080\nlive_resolution=0\n')
# The setup measured on October 21, 2026 (docs/runtime.md): unpaced vblank, a larger staging
# pool, a wider write-fault window, and no Retina scaling of the window.
TUNED = ('BB_VBLANK_HZ=0', 'BB_STAGING_KEEP_MB=2048', 'BB_FAULT_WINDOW=1024', 'BB_RETINA=0')
ENV_KEY = re.compile(r'^(BB|MESA)_[A-Z0-9_]+$')


def parse_env(values):
    """Accept only KEY=VALUE overrides for the runtime (BB_*) and the shader cache (MESA_*)."""
    for value in values:
        key, separator, _ = value.partition('=')
        if not separator or not ENV_KEY.match(key):
            raise ValueError(f'--env expects BB_* or MESA_* KEY=VALUE, got {value!r}')
    return list(values)


def runtime_environment(data, libraries, fps_size=1, frame_stats=False, extra=()):
    """Keep Bloodborne patches and diagnostics out of ordinary DS3 sessions."""
    env = {key: value for key, value in os.environ.items() if not key.startswith('BB_')}
    cache = Path(__file__).resolve().parent / 'runtime/cache/mesa'
    cache.mkdir(parents=True, exist_ok=True)
    env.update(BB_FULLSCREEN='0', BB_OBJECT_MOTION='0', BB_VBLANK_HZ='60',
               MESA_SHADER_CACHE_DIR=str(cache), MESA_SHADER_CACHE_MAX_SIZE='4G')
    env.update(value.split('=', 1) for value in extra)
    env.update(BB_CONFIG=str(data / 'bbport.ini'), BB_FPS_SCALE=str(fps_size),
               BB_VULKAN_LIBRARY=str(libraries / 'libvulkan.1.dylib'),
               SDL_VULKAN_LIBRARY=str(libraries / 'libvulkan.1.dylib'),
               VK_DRIVER_FILES=str(libraries / 'kosmickrisp/kosmickrisp_mesa_icd.json'))
    if frame_stats:
        env.update(BB_FRAME_STATS='1', BB_FRAME_LOG=str(data / 'out/frames.csv'))
    return env


def make_test_app(probe, libraries, data):
    """Give the isolated test its own Mac app identity for focus and input."""
    contents = data / 'DS3 Test.app' / 'Contents'
    binary = contents / 'MacOS' / 'bb-probe'
    binary.parent.mkdir(parents=True)
    shutil.copy2(probe, binary)
    (contents / 'lib').symlink_to(libraries, target_is_directory=True)
    (binary.parent / 'gpu').symlink_to(probe.parent / 'gpu', target_is_directory=True)
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
    engine = parser.add_mutually_exclusive_group()
    engine.add_argument('--bbport', type=Path, default=Path.home() / 'Documents/bloodborne/runtime/engines/bbport-0.4-v1/bbport.app/Contents/Resources/bbport')
    engine.add_argument('--bbport-src', type=Path, help='Use a built bbport 0.4-v1 checkout with deps-x86_64')
    parser.add_argument('--reference-game', type=Path, default=Path.home() / 'Documents/bloodborne/runtime/games/CUSA00900-109')
    parser.add_argument('--data', type=Path)
    parser.add_argument('--save-from', type=Path, help='Copy a prior test user folder into the fresh run')
    parser.add_argument('--timeout', type=int, default=120, help='Stop after 1–600 seconds; 0 runs until you quit')
    parser.add_argument('--fps-size', type=int, choices=range(1, 7), default=1,
                        help='FPS counter scale; above 1 needs the optional bbport overlay patch')
    parser.add_argument('--frame-stats', action='store_true', help='Enable diagnostic counters and frame CSV')
    parser.add_argument('--patches', type=Path, help='Owner-supplied BBPATCH2 file, copied into the session and passed to the probe')
    parser.add_argument('--tuned', action='store_true', help='Apply the measured October 21 runtime setup')
    parser.add_argument('--env', action='append', default=[], metavar='KEY=VALUE',
                        help='Runtime (BB_*) or shader cache (MESA_*) override; repeatable, applied after --tuned')
    args = parser.parse_args()
    try:
        extras = [*(TUNED if args.tuned else ()), *parse_env(args.env)]
    except ValueError as error:
        parser.error(str(error))
    if not 0 <= args.timeout <= 600:
        parser.error('--timeout must be between 0 and 600 seconds')
    if args.fps_size > 1 and not args.bbport_src:
        parser.error('--fps-size above 1 needs --bbport-src with the optional overlay patch')
    if subprocess.run(['pgrep', '-x', 'bb-probe'], stdout=subprocess.DEVNULL).returncode == 0:
        parser.error('Close the running bbport test or game first')
    game, root, reference = (p.expanduser().resolve() for p in (args.game, args.bbport_src or args.bbport, args.reference_game))
    patches = args.patches.expanduser().resolve() if args.patches else None
    if patches and not patches.is_file():
        parser.error(f'Missing input: {patches}')
    probe = root / ('out/bb-probe' if args.bbport_src else 'bin/bb-probe')
    libraries = root / ('deps-x86_64/lib' if args.bbport_src else 'lib')
    for p in (game / 'eboot.bin', game / 'sce_sys/param.sfo', reference / 'eboot.bin', probe,
              probe.parent / 'gpu/libbbgpu.dylib', libraries / 'libvulkan.1.dylib',
              libraries / 'kosmickrisp/kosmickrisp_mesa_icd.json',
              root / 'scripts/link_modules.py', root / 'scripts/prepare.py',
              root / 'scripts/game_check.py', root / 'scripts/content_profile.py'):
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
    (data / 'bbport.ini').write_text(DEFAULT_SETTINGS)
    if patches:
        shutil.copy2(patches, out / 'patches.bin')
    binary = make_test_app(probe, libraries, data)
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
    env = runtime_environment(data, libraries, args.fps_size, args.frame_stats, extras)
    subprocess.run([sys.executable, str(root / 'scripts/content_profile.py'), str(game), '--out', str(out)],
                   env=env, check=True)
    command = [str(binary), str(out / 'boot-ds3.bin'),
               '--content-profile', str(out / 'content.bin'), '--app0', str(game),
               '--user', str(data / 'user'),
               *(['--patches', str(out / 'patches.bin')] if patches else []),
               '--timeout', str(args.timeout)]
    report = {'title': info['TITLE'], 'title_id': info['TITLE_ID'], 'version': info['APP_VER'],
              'game': str(game), 'bbport': str(root), 'remapped_imports': len(changes),
              'runtime_layout': 'source' if args.bbport_src else 'packaged',
              'timeout_seconds': args.timeout, 'gameplay_verified': False, 'extra_env': extras,
              'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
              'app_probe_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
              'gpu_sha256': hashlib.sha256((probe.parent / 'gpu/libbbgpu.dylib').read_bytes()).hexdigest()}
    if patches:
        report['patches_sha256'] = hashlib.sha256((out / 'patches.bin').read_bytes()).hexdigest()
    duration = f'{args.timeout}-second test' if args.timeout else 'session until you quit'
    print(f'Remapped {len(changes)} imports. Starting {duration}. Log: {out / "run.log"}', flush=True)
    with (out / 'run.log').open('w') as log:
        try:
            result = subprocess.run(command, env=env, cwd=root, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=args.timeout + 15 if args.timeout else None)
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
