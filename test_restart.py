# SPDX-License-Identifier: MIT
# Copyright (c) 2026 CSR (Celaya Solutions)
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import restart


class RestartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="DS3 user's ")
        self.addCleanup(self.temp.cleanup)
        self.data = Path(self.temp.name)
        self.binary = self.data / 'DS3 Test.app/Contents/MacOS/bb-probe'
        self.gpu = self.binary.parent / 'gpu/libbbgpu.dylib'
        self.save = self.data / 'user/savedata/1/CUSA03388/DS30000/save'
        for path in (self.binary, self.gpu, self.save, self.data / 'out/boot-ds3.bin',
                     self.data / 'out/content.bin', self.data / 'bbport.ini',
                     self.data / 'game/eboot.bin',
                     self.data / 'DS3 Test.app/Contents/lib/libvulkan.1.dylib',
                     self.data / 'DS3 Test.app/Contents/lib/kosmickrisp/kosmickrisp_mesa_icd.json'):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'original')
        self.binary.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
Path('environment.json').write_text(json.dumps(dict(os.environ)))
Path('arguments.json').write_text(json.dumps(sys.argv[1:]))
Path('user/savedata/1/CUSA03388/DS30000/save').write_bytes(b'new progress')
print('test runtime')
''')
        self.binary.chmod(0o755)
        self.report = self.data / 'out/result.json'
        self.report.write_text(json.dumps({
            'title_id': 'CUSA03388', 'version': '01.00', 'runtime_layout': 'source',
            'game': str(self.data / 'game'), 'bbport': str(self.data),
            'app_probe_sha256': hashlib.sha256(self.binary.read_bytes()).hexdigest(),
            'gpu_sha256': hashlib.sha256(self.gpu.read_bytes()).hexdigest(),
        }))
        self.report_before = self.report.read_bytes()
        self.pgrep = self.data / 'bin/pgrep'
        self.pgrep.parent.mkdir()
        self.pgrep.write_text('#!/bin/sh\nexit 1\n')
        self.pgrep.chmod(0o755)

    def run_restart(self, *options):
        import os
        env = dict(os.environ, PATH=str(self.pgrep.parent) + os.pathsep + os.environ['PATH'],
                   BB_PATCHES='unsafe', BB_FRAME_STATS='1', BB_FRAME_LOG='/tmp/old.csv')
        return subprocess.run([sys.executable, str(Path(restart.__file__)), str(self.data),
                               '--fps-size', '3', *options], env=env, capture_output=True, text=True)

    def test_restart_replays_recorded_extras_unless_overridden(self):
        report = json.loads(self.report.read_text())
        report['extra_env'] = ['BB_VBLANK_HZ=0', 'BB_STAGING_KEEP_MB=2048']
        self.report.write_text(json.dumps(report))
        self.report_before = self.report.read_bytes()
        self.assertEqual(self.run_restart().returncode, 0)
        env = json.loads((self.data / 'environment.json').read_text())
        self.assertEqual((env['BB_VBLANK_HZ'], env['BB_STAGING_KEEP_MB']), ('0', '2048'))
        self.assertEqual(self.run_restart('--env', 'BB_VBLANK_HZ=30').returncode, 0)
        env = json.loads((self.data / 'environment.json').read_text())
        self.assertEqual(env['BB_VBLANK_HZ'], '30')
        self.assertNotIn('BB_STAGING_KEEP_MB', env)
        self.assertEqual(self.run_restart('--env', 'FOO=1').returncode, 2)
        self.assertEqual(self.report.read_bytes(), self.report_before)

    def test_restarts_preserve_latest_progress_backups_and_original_report(self):
        for prior in (b'original', b'new progress'):
            result = self.run_restart()
            self.assertEqual(result.returncode, 0, result.stderr)
            backups = sorted((self.data / 'backups').iterdir())
            self.assertEqual((backups[-1] / self.save.relative_to(self.data)).read_bytes(), prior)
            self.assertEqual((backups[-1] / 'bbport.ini').read_bytes(), b'original')
            self.assertEqual(self.save.read_bytes(), b'new progress')
        self.assertEqual(len(backups), 2)
        self.assertEqual(len(list((self.data / 'out').glob('play-*.log'))), 2)
        self.assertEqual(self.report.read_bytes(), self.report_before)
        env = json.loads((self.data / 'environment.json').read_text())
        self.assertFalse({'BB_PATCHES', 'BB_FRAME_STATS', 'BB_FRAME_LOG'} & env.keys())
        self.assertEqual(env['BB_FPS_SCALE'], '3')

    def test_changed_runtime_and_missing_files_fail_before_save_or_backup_changes(self):
        self.gpu.write_bytes(b'changed')
        self.assertIn('Runtime changed', self.run_restart().stderr)
        self.gpu.unlink()
        self.assertIn('Missing input', self.run_restart().stderr)
        self.assertFalse((self.data / 'backups').exists())
        self.assertEqual(self.save.read_bytes(), b'original')

    def test_running_game_and_duplicate_shortcut_fail_before_backup(self):
        with (self.data / '.play.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertIn('already running', self.run_restart().stderr)
        self.pgrep.write_text('#!/bin/sh\nexit 0\n')
        self.assertIn('Close the running bbport', self.run_restart().stderr)
        self.assertFalse((self.data / 'backups').exists())

    def test_invalid_report_fails_without_starting_runtime(self):
        older_report = json.loads(self.report_before)
        del older_report['app_probe_sha256']
        self.report.write_text(json.dumps(older_report))
        self.assertIn('Older session report', self.run_restart().stderr)
        for report in ('invalid json', '{}', '{"title_id":"CUSA00900","version":"01.09"}'):
            self.report.write_text(report)
            self.assertNotEqual(self.run_restart().returncode, 0)
        self.assertFalse((self.data / 'backups').exists())

    def test_backup_failure_prevents_launch(self):
        with patch.object(sys, 'argv', ['restart.py', str(self.data)]), \
                patch.object(restart.subprocess, 'run') as run, \
                patch.object(restart.shutil, 'copytree', side_effect=OSError('disk full')), \
                self.assertRaises(SystemExit):
            run.return_value.returncode = 1
            restart.main()
        self.assertEqual(run.call_count, 1)
        self.assertEqual(self.save.read_bytes(), b'original')


if __name__ == '__main__':
    unittest.main()
