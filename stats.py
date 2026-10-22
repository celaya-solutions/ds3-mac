#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 CSR (Celaya Solutions)
"""Summarize a bbport frame CSV: gameplay rows only, FPS percentiles, hitches, counters."""
import argparse
import csv
import json
import math
import statistics
import sys

COLUMNS = ('t_s', 'frame_ms', 'write_fault_ms', 'draws', 'compiles', 'image_mb')


def gameplay_rows(path, min_draws=500):
    """Rows whose draw count is above `min_draws` (menus and loads draw little), values as floats."""
    with open(path, newline='') as file:
        reader = csv.DictReader(file)
        for name in COLUMNS:
            if name not in (reader.fieldnames or ()):
                raise ValueError(f'Missing column {name} in {path}')
        rows = [{key: float(value) for key, value in row.items() if value not in ('', None)}
                for row in reader]
    return [row for row in rows if row.get('draws', 0) > min_draws]


def percentile(values, p):
    """Nearest-rank percentile."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p / 100 * len(ordered)) - 1)]


def summarize(rows, hitch_ms=50.0):
    if not rows:
        raise ValueError('No gameplay rows')
    frame_ms = [row['frame_ms'] for row in rows]
    return {
        'frames': len(rows),
        'seconds': round(rows[-1]['t_s'] - rows[0]['t_s'], 1),
        'median_fps': round(1000 / percentile(frame_ms, 50), 1),
        'p10_fps': round(1000 / percentile(frame_ms, 90), 1),
        'p1_fps': round(1000 / percentile(frame_ms, 99), 1),
        'hitches': sum(ms > hitch_ms for ms in frame_ms),
        'write_fault_ms': round(statistics.median(row['write_fault_ms'] for row in rows), 1),
        'compiles': int(sum(row['compiles'] for row in rows)),
        'image_mb': round(sum(row['image_mb'] for row in rows), 1),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', help='frames.csv written with BB_FRAME_STATS=1')
    parser.add_argument('--min-draws', type=int, default=500)
    parser.add_argument('--hitch-ms', type=float, default=50.0)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        rows = gameplay_rows(args.csv, args.min_draws)
    except (OSError, ValueError) as error:
        sys.exit(str(error))
    if not rows:
        sys.exit(f'No gameplay rows in {args.csv}')
    summary = summarize(rows, args.hitch_ms)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for key, value in summary.items():
            print(f'{key}: {value}')


if __name__ == '__main__':
    main()
