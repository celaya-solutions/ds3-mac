# SPDX-License-Identifier: MIT
# Copyright (c) 2026 CSR (Celaya Solutions)
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import stats


class StatsTests(unittest.TestCase):
    HEADER = 't_s,frame_ms,write_fault_ms,draws,compiles,image_mb\n'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def write(self, rows, header=HEADER, name='frames.csv'):
        path = Path(self.temp.name) / name
        path.write_text(header + ''.join(','.join(str(v) for v in row) + '\n' for row in rows))
        return path

    def test_summary_uses_gameplay_rows_only(self):
        rows = [(0, 100, 0, 10, 5, 1)] + [(i, 20, 10, 800, 0, 2) for i in range(1, 9)] + [(9, 60, 30, 800, 1, 16)]
        summary = stats.summarize(stats.gameplay_rows(self.write(rows)))
        self.assertEqual(summary['frames'], 9)
        self.assertEqual(summary['seconds'], 8.0)
        self.assertEqual(summary['median_fps'], 50.0)
        self.assertEqual(summary['p10_fps'], 16.7)
        self.assertEqual(summary['p1_fps'], 16.7)
        self.assertEqual(summary['hitches'], 1)
        self.assertEqual(summary['write_fault_ms'], 10.0)
        self.assertEqual(summary['compiles'], 1)
        self.assertEqual(summary['image_mb'], 32.0)

    def test_cli_reports_missing_column_and_no_rows(self):
        empty = self.write([(0, 100, 0, 10, 0, 0)])
        result = subprocess.run([sys.executable, 'stats.py', str(empty)], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stderr.strip()), (1, f'No gameplay rows in {empty}'))
        short = self.write([(0, 20, 800, 0, 1)], header='t_s,frame_ms,draws,compiles,image_mb\n', name='short.csv')
        result = subprocess.run([sys.executable, 'stats.py', str(short)], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stderr.strip()), (1, f'Missing column write_fault_ms in {short}'))

    def test_presented_fps_appears_only_with_the_presented_column(self):
        rows = [(i, 25, 5, 900, 0, 1) for i in range(5)]
        self.assertNotIn('presented_fps', stats.summarize(stats.gameplay_rows(self.write(rows))))
        header = 't_s,frame_ms,write_fault_ms,draws,compiles,image_mb,presented\n'
        doubled = self.write([(*row, 2) for row in rows], header=header, name='doubled.csv')
        self.assertEqual(stats.summarize(stats.gameplay_rows(doubled))['presented_fps'], 2.5)

    def test_cli_prints_one_line_per_key_and_json(self):
        path = self.write([(i, 25, 5, 900, 0, 1) for i in range(4)])
        result = subprocess.run([sys.executable, 'stats.py', str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('median_fps: 40.0\n', result.stdout)
        result = subprocess.run([sys.executable, 'stats.py', str(path), '--json'], capture_output=True, text=True)
        self.assertIn('"median_fps": 40.0', result.stdout)


if __name__ == '__main__':
    unittest.main()
