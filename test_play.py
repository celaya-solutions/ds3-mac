import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import play


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.game = self.root / 'game'
        self.reference = self.root / 'reference'
        self.engine = self.root / 'engine'
        self.data = self.root / 'session'
        self.save = self.root / 'prior/user'
        self.save_file = self.save / 'savedata/1/CUSA03388/DS30000/userdata0000'
        for path in (self.game / 'eboot.bin', self.game / 'sce_sys/param.sfo',
                     self.reference / 'eboot.bin', self.save_file):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'original')
        self.modules = {
            'prepare': SimpleNamespace(sfo=lambda _: {'TITLE': 'DS3', 'TITLE_ID': 'CUSA03388',
                                                     'APP_VER': '01.00'}, prepare=lambda *_: None),
            'game_check': SimpleNamespace(image_sha256=lambda _: 'supported', SUPPORTED_IMAGE='supported'),
            'link_modules': SimpleNamespace(module=lambda _: {}, link=lambda *_: None),
        }
        self.addCleanup(setattr, sys, 'path', sys.path[:])
        self.addCleanup(setattr, sys, 'dont_write_bytecode', sys.dont_write_bytecode)
        self.launches = []
        self.signs = []

    def make_engine(self, source):
        probe = self.engine / ('out/bb-probe' if source else 'bin/bb-probe')
        libraries = self.engine / ('deps-x86_64/lib' if source else 'lib')
        for path in (probe, probe.parent / 'gpu/libbbgpu.dylib', libraries / 'libvulkan.1.dylib',
                     libraries / 'kosmickrisp/kosmickrisp_mesa_icd.json',
                     *(self.engine / 'scripts' / name for name in
                       ('prepare.py', 'game_check.py', 'link_modules.py', 'content_profile.py'))):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'runtime')
        return probe, libraries

    def run_command(self, command, **kwargs):
        if command[0] == 'pgrep':
            return SimpleNamespace(returncode=1)
        if command[0] == 'codesign':
            self.signs.append(command)
            binary = Path(command[-1]) / 'Contents/MacOS/bb-probe'
            binary.write_bytes(binary.read_bytes() + b'-signed')
        if command[0].endswith('/MacOS/bb-probe'):
            self.launches.append((command, kwargs))
            kwargs['stdout'].write('Entering original x86-64 code\n')
        return SimpleNamespace(returncode=0)

    def launch(self, *options):
        argv = ['play.py', '--game', str(self.game), '--reference-game', str(self.reference),
                '--data', str(self.data), '--save-from', str(self.save), *options]
        with patch.object(sys, 'argv', argv), patch.dict(sys.modules, self.modules), \
                patch.object(play.subprocess, 'run', side_effect=self.run_command), \
                patch.object(play, 'adapt_image', return_value=[]), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return play.main()

    def test_both_layouts_keep_copied_save_and_use_matching_metal_libraries(self):
        for source in (False, True):
            with self.subTest(source=source):
                self.data = self.root / ('source-session' if source else 'release-session')
                probe, libraries = self.make_engine(source)
                option = '--bbport-src' if source else '--bbport'
                with patch.dict(os.environ, {'BB_PATCHES': 'Bloodborne patch', 'BB_FPS': '90',
                                             'BB_RENDER_RES': '2560x1440', 'BB_FPS_SCALE': '6',
                                             'BB_FRAME_STATS': '1', 'BB_FRAME_LOG': '/tmp/old.csv'}):
                    self.assertEqual(self.launch(option, str(self.engine)), 0)
                command, kwargs = self.launches[-1]
                env = kwargs['env']
                self.assertEqual(env['VK_DRIVER_FILES'], str(libraries / 'kosmickrisp/kosmickrisp_mesa_icd.json'))
                self.assertEqual(env['BB_VULKAN_LIBRARY'], str(libraries / 'libvulkan.1.dylib'))
                self.assertEqual(env['SDL_VULKAN_LIBRARY'], env['BB_VULKAN_LIBRARY'])
                self.assertEqual(env['BB_FPS_SCALE'], '1')
                self.assertNotIn('BB_FRAME_STATS', env)
                self.assertNotIn('BB_FRAME_LOG', env)
                self.assertEqual((self.data / 'bbport.ini').read_text(), play.DEFAULT_SETTINGS)
                self.assertIn('upscaler=metalfx\npreset=0\n', play.DEFAULT_SETTINGS)
                self.assertFalse({'BB_PATCHES', 'BB_FPS', 'BB_RENDER_RES'} & env.keys())
                self.assertNotIn('--patches', command)
                self.assertEqual(command[-2:], ['--timeout', '120'])
                self.assertEqual(kwargs['timeout'], 135)
                binary = Path(command[0])
                self.assertEqual(binary.read_bytes(), probe.read_bytes() + b'-signed')
                self.assertEqual((binary.parent / 'gpu').resolve(), probe.parent / 'gpu')
                self.assertEqual((binary.parents[1] / 'lib').resolve(), libraries)
                self.assertNotIn('--deep', self.signs[-1])
                copied = self.data / 'user' / self.save_file.relative_to(self.save)
                self.assertEqual(copied.read_bytes(), b'original')
                copied.write_bytes(b'new progress')
                self.assertEqual(self.save_file.read_bytes(), b'original')
                report = json.loads((self.data / 'out/result.json').read_text())
                self.assertEqual(report['runtime_layout'], 'source' if source else 'packaged')
                self.assertEqual(report['app_probe_sha256'], hashlib.sha256(binary.read_bytes()).hexdigest())
                self.assertNotEqual(report['probe_sha256'], report['app_probe_sha256'])
                self.assertEqual(len(report['gpu_sha256']), 64)
                self.assertTrue(report['entered_game'])
                self.assertFalse(report['gameplay_verified'])

    def test_source_counter_scale_and_no_watchdog(self):
        self.make_engine(True)
        self.assertEqual(self.launch('--bbport-src', str(self.engine), '--fps-size', '3',
                                     '--timeout', '0', '--frame-stats'), 0)
        command, kwargs = self.launches[-1]
        self.assertEqual(command[-2:], ['--timeout', '0'])
        self.assertIsNone(kwargs['timeout'])
        self.assertEqual(kwargs['env']['BB_FPS_SCALE'], '3')
        self.assertEqual(kwargs['env']['BB_FRAME_STATS'], '1')
        self.assertEqual(kwargs['env']['BB_FRAME_LOG'], str(self.data / 'out/frames.csv'))

    def test_tuned_and_env_override_defaults_but_not_session_paths(self):
        self.make_engine(True)
        self.assertEqual(self.launch('--bbport-src', str(self.engine), '--tuned',
                                     '--env', 'BB_VBLANK_HZ=30', '--env', 'BB_CONFIG=/elsewhere'), 0)
        env = self.launches[-1][1]['env']
        self.assertEqual(env['BB_VBLANK_HZ'], '30')
        self.assertEqual(env['BB_STAGING_KEEP_MB'], '2048')
        self.assertEqual(env['BB_FAULT_WINDOW'], '1024')
        self.assertEqual(env['BB_RETINA'], '0')
        self.assertEqual(env['BB_CONFIG'], str(self.data / 'bbport.ini'))
        self.assertEqual(env['MESA_SHADER_CACHE_MAX_SIZE'], '4G')
        self.assertTrue(Path(env['MESA_SHADER_CACHE_DIR']).is_dir())
        report = json.loads((self.data / 'out/result.json').read_text())
        self.assertEqual(report['extra_env'], [*play.TUNED, 'BB_VBLANK_HZ=30', 'BB_CONFIG=/elsewhere'])

    def test_untuned_session_keeps_60_hz_vblank_and_records_empty_extras(self):
        self.make_engine(True)
        self.assertEqual(self.launch('--bbport-src', str(self.engine)), 0)
        self.assertEqual(self.launches[-1][1]['env']['BB_VBLANK_HZ'], '60')
        self.assertEqual(json.loads((self.data / 'out/result.json').read_text())['extra_env'], [])

    def test_patch_file_is_copied_passed_and_hashed(self):
        self.make_engine(True)
        patch = self.root / 'limiter.bin'
        patch.write_bytes(b'BBPATCH2 test')
        self.assertEqual(self.launch('--bbport-src', str(self.engine), '--patches', str(patch)), 0)
        command = self.launches[-1][0]
        copied = self.data / 'out/patches.bin'
        self.assertEqual(command[command.index('--patches') + 1], str(copied))
        self.assertEqual(copied.read_bytes(), b'BBPATCH2 test')
        report = json.loads((self.data / 'out/result.json').read_text())
        self.assertEqual(report['patches_sha256'], hashlib.sha256(b'BBPATCH2 test').hexdigest())

    def test_invalid_options_and_missing_gpu_fail_before_creating_session(self):
        probe, _ = self.make_engine(True)
        (probe.parent / 'gpu/libbbgpu.dylib').unlink()
        for options in (['--bbport-src', str(self.engine)],
                        ['--bbport', str(self.engine), '--fps-size', '2'],
                        ['--bbport', str(self.engine), '--bbport-src', str(self.engine)],
                        ['--timeout', '-1'], ['--timeout', '601'], ['--fps-size', '7'],
                        ['--env', 'FOO=1'], ['--env', 'BB_X'], ['--env', 'PATH=/x'],
                        ['--patches', str(self.root / 'missing.bin')]):
            with self.subTest(options=options), self.assertRaises(SystemExit):
                self.launch(*options)
            self.assertFalse(self.data.exists())

    def test_existing_session_and_wrong_reference_are_preserved(self):
        self.make_engine(True)
        self.modules['game_check'].image_sha256 = lambda _: 'wrong'
        with self.assertRaises(SystemExit):
            self.launch('--bbport-src', str(self.engine))
        self.assertFalse(self.data.exists())
        self.modules['game_check'].image_sha256 = lambda _: 'supported'
        self.data.mkdir()
        marker = self.data / 'keep'
        marker.write_bytes(b'keep')
        with self.assertRaises(SystemExit):
            self.launch('--bbport-src', str(self.engine))
        self.assertEqual(marker.read_bytes(), b'keep')
        self.assertEqual(self.launches, [])

    def test_host_watchdog_records_failure(self):
        self.make_engine(True)
        normal_run = self.run_command

        def timed_out(command, **kwargs):
            if command[0].endswith('/MacOS/bb-probe'):
                raise subprocess.TimeoutExpired(command, kwargs['timeout'])
            return normal_run(command, **kwargs)

        self.run_command = timed_out
        self.assertEqual(self.launch('--bbport-src', str(self.engine)), 124)
        report = json.loads((self.data / 'out/result.json').read_text())
        self.assertTrue(report['host_timeout'])


if __name__ == '__main__':
    unittest.main()
