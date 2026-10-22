```text
Document:    DS3 on Mac — Launcher Tuning Implementation Plan
Version:     v1.0.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-21
SHA256:      5e2399fb0ff31e601344dad79a94ec27e8f9ed8f560cd3f3efba879bab302253
Chain:       solana-mainnet
Tx:          4Bq4CpYPEiXcXCNDfe8DqDgJLa2F1N7eqpcFJhLAdzyPVFR9D3Xu8b1ePV85T6trKJnoKRp1KPLeTRpDYE3fgGLk
License:     MIT / CSR (Celaya Solutions)
```

# Launcher Tuning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The launchers reproduce the measured October 21 setup, default to MetalFX anti-aliasing, and report frame statistics from a checked-in script.

**Architecture:** `play.py` keeps one function, `runtime_environment`, that builds the probe's environment; it gains an ordered override list and the shader-cache pin. `restart.py` reads what `play.py` recorded in `result.json` so the Desktop shortcut needs no new flags. `stats.py` is a standalone reader of bbport's frame CSV.

**Tech Stack:** Python 3.9 standard library, `unittest`.

**Spec:** `docs/superpowers/specs/2026-10-21-metal-performance-design.md`

## Global Constraints

- Python 3.9+, standard library only. `python3 -m unittest -v` and `git diff --check` pass after every task.
- Every `BB_*` variable from the caller's shell is still dropped; only `--tuned` and `--env` reach the probe.
- The session's `bbport.ini`, Vulkan library paths and `VK_DRIVER_FILES` always win over `--env`.
- No Bloodborne patch, resolution or frame-rate variable is ever set by default.
- Documents carry the standard header; run `docseal anchor` on changed header-bearing files before each commit.

## Review Focus

- `--env` with a key outside `BB_*`/`MESA_*`, or without `=`: the launcher refuses before creating a session (Task 1 test).
- `--env BB_CONFIG=/elsewhere`: the session ini path still wins (Task 1 test).
- `restart.py` on a session recorded before this change (no `extra_env`, no `patches_sha256`): launches as before, no patch file (Task 2 test).
- A patch file edited after the session was prepared: `restart.py` refuses with "Patch file changed" (Task 2 test).
- A frame CSV with no gameplay rows or a missing column: `stats.py` exits 1 with a one-line message, no traceback (Task 3 test).

---

### Task 1: `--tuned`, `--env`, shader-cache pin

**Files:**
- Modify: `play.py:21-31` (`runtime_environment`), `play.py:52-70` (arguments), `play.py:128-136` (report)
- Modify: `restart.py:17-24` (arguments), `restart.py:66-69` (launch)
- Test: `test_play.py`, `test_restart.py`

**Interfaces:**
- Produces: `TUNED = ('BB_VBLANK_HZ=0', 'BB_STAGING_KEEP_MB=2048', 'BB_FAULT_WINDOW=1024', 'BB_RETINA=0')` in `play.py`.
- Produces: `runtime_environment(data, libraries, fps_size=1, frame_stats=False, extra=())` where `extra` is a sequence of `KEY=VALUE` strings applied in order after the defaults (`BB_VBLANK_HZ=60`, `BB_FULLSCREEN=0`, `BB_OBJECT_MOTION=0`) and before the fixed keys (`BB_CONFIG`, `BB_FPS_SCALE`, `BB_VULKAN_LIBRARY`, `SDL_VULKAN_LIBRARY`, `VK_DRIVER_FILES`, frame stats).
- Produces: `parse_env(values)` in `play.py`: validates each string (`KEY=VALUE`, key matches `^(BB|MESA)_[A-Z0-9_]+$`), returns the list unchanged, raises `ValueError` with the offending string.
- Produces: `result.json` key `extra_env` (list of strings, `TUNED` expanded first when `--tuned`).
- Shader cache: `runtime_environment` sets `MESA_SHADER_CACHE_DIR` to `<repo>/runtime/cache/mesa` (created) and `MESA_SHADER_CACHE_MAX_SIZE=4G` before `extra`.

- [ ] **Step 1: Write the failing tests in `test_play.py`**

```python
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
```

Add to `test_invalid_options_and_missing_gpu_fail_before_creating_session` options: `['--env', 'FOO=1']`, `['--env', 'BB_X']`, `['--env', 'PATH=/x']`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest test_play -v`
Expected: the two new tests FAIL (`unrecognized arguments: --tuned`); the invalid-option subtests FAIL (no `SystemExit`).

- [ ] **Step 3: Implement in `play.py`**

Add `TUNED`, `parse_env(values)`, the `extra` parameter and the cache pin to `runtime_environment`; add `--tuned` (store_true) and `--env` (action `append`, default `[]`, metavar `KEY=VALUE`); build `extras = [*(TUNED if args.tuned else ()), *parse_env(args.env)]`, pass it to `runtime_environment`, record `report['extra_env'] = extras`. A `ValueError` from `parse_env` becomes `parser.error`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest test_play -v`
Expected: PASS, all tests.

- [ ] **Step 5: Write the failing tests in `test_restart.py`**

Change the fake binary in `setUp` to also write `arguments.json` (`json.dumps(sys.argv[1:])`). Add `extra` to `run_restart(self, *options)` so callers can pass flags.

```python
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
```

- [ ] **Step 6: Run to verify it fails**

Run: `python3 -m unittest test_restart -v`
Expected: FAIL (`unrecognized arguments: --env`).

- [ ] **Step 7: Implement in `restart.py`**

Add `--tuned` and `--env` (same definitions, import `TUNED` and `parse_env` from `play`). `extras = [*(TUNED if args.tuned else ()), *parse_env(args.env)]` when either flag is given, else `report.get('extra_env', [])`. Pass `extra=extras` to `runtime_environment`.

- [ ] **Step 8: Run the whole suite**

Run: `python3 -m unittest -v && git diff --check`
Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add play.py restart.py test_play.py test_restart.py
git commit -m "Add --tuned and --env launcher knobs and pin the Mesa shader cache"
```

---

### Task 2: `--patches FILE`

**Files:**
- Modify: `play.py` (argument, copy, command, report), `restart.py` (command, check)
- Test: `test_play.py`, `test_restart.py`

**Interfaces:**
- Consumes: Task 1's `arguments.json` fake binary.
- Produces: `--patches FILE` on `play.py`: the file is copied to `<session>/out/patches.bin`; the probe command gains `['--patches', str(out / 'patches.bin')]` before `--timeout`; `result.json` gains `patches_sha256` (hex of the copied file). Without the flag the key is absent and the command has no `--patches`.
- Produces: `restart.py` passes `--patches <session>/out/patches.bin` when `report['patches_sha256']` is present; it refuses with `Patch file changed; prepare a fresh session with play.py --save-from first` when the file's hash differs or the file is missing.

- [ ] **Step 1: Write the failing tests**

`test_play.py`:

```python
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
```

Add `['--patches', str(self.root / 'missing.bin')]` to the invalid-option subtests.

`test_restart.py`:

```python
def test_patch_file_is_passed_when_recorded_and_refused_when_changed(self):
    self.assertEqual(self.run_restart().returncode, 0)
    self.assertNotIn('--patches', json.loads((self.data / 'arguments.json').read_text()))
    patch = self.data / 'out/patches.bin'
    patch.write_bytes(b'BBPATCH2 test')
    report = json.loads(self.report.read_text())
    report['patches_sha256'] = hashlib.sha256(b'BBPATCH2 test').hexdigest()
    self.report.write_text(json.dumps(report))
    self.report_before = self.report.read_bytes()
    self.assertEqual(self.run_restart().returncode, 0)
    arguments = json.loads((self.data / 'arguments.json').read_text())
    self.assertEqual(arguments[arguments.index('--patches') + 1], str(patch))
    patch.write_bytes(b'edited')
    result = self.run_restart()
    self.assertEqual(result.returncode, 2)
    self.assertIn('Patch file changed', result.stderr)
    self.assertEqual(len(list((self.data / 'backups').iterdir())), 2)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest test_play test_restart -v`
Expected: FAIL (`unrecognized arguments: --patches`; `--patches` not in arguments).

- [ ] **Step 3: Implement**

`play.py`: `--patches` (type `Path`); add it to the missing-input loop when given; `shutil.copy2` into `out/patches.bin` after `out.mkdir`; extend `command`; set `report['patches_sha256']`. `restart.py`: after the hash loop, if `'patches_sha256' in report`, check `out/patches.bin` exists and hashes equal, else `parser.error(...)`; append `['--patches', str(patches)]` to `command`.

- [ ] **Step 4: Run the whole suite**

Run: `python3 -m unittest -v && git diff --check`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add play.py restart.py test_play.py test_restart.py
git commit -m "Pass an owner-supplied patch file through play.py and restart.py"
```

---

### Task 3: `stats.py`

**Files:**
- Create: `stats.py`
- Test: `test_stats.py`

**Interfaces:**
- Produces: `gameplay_rows(path, min_draws=500) -> list[dict]` (rows whose `draws` > `min_draws`, values as floats).
- Produces: `summarize(rows, hitch_ms=50.0) -> dict` with keys `frames`, `seconds` (last `t_s` minus first), `median_fps`, `p10_fps`, `p1_fps` (1000 divided by the 50th, 90th and 99th nearest-rank percentile of `frame_ms`), `hitches` (rows with `frame_ms` > `hitch_ms`), `write_fault_ms` (median), `compiles` (sum), `image_mb` (sum). Values rounded to one decimal.
- Produces: CLI `python3 stats.py FRAMES.csv [--min-draws N] [--hitch-ms MS] [--json]`; prints one `key: value` line per key, or the dict as JSON; exits 1 with `No gameplay rows in <path>` or `Missing column <name> in <path>`.

- [ ] **Step 1: Write the failing test**

```python
class StatsTests(unittest.TestCase):
    HEADER = 't_s,frame_ms,write_fault_ms,draws,compiles,image_mb\n'

    def write(self, rows):
        path = Path(self.temp.name) / 'frames.csv'
        path.write_text(self.HEADER + ''.join(f'{t},{f},{w},{d},{c},{i}\n' for t, f, w, d, c, i in rows))
        return path

    def test_summary_uses_gameplay_rows_only(self):
        rows = [(0, 100, 0, 10, 5, 1)] + [(i, 20, 10, 800, 0, 2) for i in range(1, 9)] + [(9, 60, 30, 800, 1, 16)]
        summary = stats.summarize(stats.gameplay_rows(self.write(rows)))
        self.assertEqual(summary['frames'], 9)
        self.assertEqual(summary['seconds'], 8.0)
        self.assertEqual(summary['median_fps'], 50.0)
        self.assertEqual(summary['p10_fps'], 16.7)
        self.assertEqual(summary['hitches'], 1)
        self.assertEqual(summary['write_fault_ms'], 10.0)
        self.assertEqual(summary['compiles'], 1)
        self.assertEqual(summary['image_mb'], 32.0)

    def test_cli_reports_missing_column_and_no_rows(self):
        empty = self.write([(0, 100, 0, 10, 0, 0)])
        result = subprocess.run([sys.executable, 'stats.py', str(empty)], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stderr.strip()), (1, f'No gameplay rows in {empty}'))
```

(`setUp` creates `self.temp`; the second test also writes a CSV without `write_fault_ms` and asserts `Missing column write_fault_ms in <path>`.)

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m unittest test_stats -v`
Expected: FAIL (`No module named 'stats'`).

- [ ] **Step 3: Implement `stats.py`**

Standard header as a module docstring comment block (MIT / CSR). `csv.DictReader`; nearest-rank percentile `sorted_values[max(0, math.ceil(p / 100 * n) - 1)]`.

- [ ] **Step 4: Run the whole suite**

Run: `python3 -m unittest -v && git diff --check`
Expected: PASS. Also run `python3 stats.py runtime/goal-native-1440p/out/frames-20261021-194836.csv` on the test machine and compare with the runtime guide's row (median 53.6, p10 42.0): values must match to one decimal.

- [ ] **Step 5: Commit**

```bash
git add stats.py test_stats.py
git commit -m "Add stats.py: frame CSV summary with gameplay filter and hitch count"
```

---

### Task 4: MetalFX Native AA by default

**Files:**
- Modify: `play.py:16-17` (`DEFAULT_SETTINGS`)
- Modify: `docs/runtime.md` (the "Fresh sessions default to..." paragraph; the stats, `--tuned`, `--env`, `--patches` and Desktop shortcut recipes)
- Modify: `README.md` (one sentence in "Current state")
- Test: `test_play.py`

**Interfaces:**
- Produces: `DEFAULT_SETTINGS = 'show_fps=1\nupscaler=metalfx\npreset=0\nobject_motion=0\noutput_res=1920x1080\nlive_resolution=0\n'`.

- [ ] **Step 1: Write the failing assertion**

In `test_both_layouts_keep_copied_save_and_use_matching_metal_libraries`, after the ini comparison add `self.assertIn('upscaler=metalfx\npreset=0\n', play.DEFAULT_SETTINGS)`.

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m unittest test_play -v`
Expected: FAIL on the new assertion.

- [ ] **Step 3: Implement**

Change `DEFAULT_SETTINGS`. Update the docs: fresh sessions default to MetalFX temporal anti-aliasing at native 1080p (preset 0, "Native AA"); document `--tuned`, `--env`, `--patches`, `stats.py`, and that the Desktop shortcut needs no change because `restart.py` replays the recorded extras. Bump each document's header version and date.

- [ ] **Step 4: Run the suite and anchor**

Run: `python3 -m unittest -v && git diff --check && docseal anchor README.md docs/runtime.md`
Expected: PASS; anchor prints both transaction signatures (or `docseal stamp` with the reason recorded in the commit).

- [ ] **Step 5: Commit**

```bash
git add play.py test_play.py docs/runtime.md README.md
git commit -m "Default new sessions to MetalFX Native AA and document the launcher knobs"
```

---

### Task 5: Owner measurements (manual, owner runs the game)

**Files:**
- Modify: `docs/runtime.md` (new section "Launcher measurements — <date>")

**Interfaces:**
- Consumes: Tasks 1–4. The builder prepares the commands; the owner plays each run and pastes `stats.py` output.

- [ ] **Step 1: Prepare a fresh session with the recorded setup**

```sh
python3 play.py --game <dump> --bbport-src ~/Documents/bbport-mac --reference-game <bloodborne> \
  --save-from runtime/desktop-play-20261021/user --patches <owner's limiter patch file> \
  --tuned --fps-size 3 --frame-stats --timeout 0
```

Expected: the log shows `Applied patch` once, the FPS counter, and `python3 stats.py <session>/out/frames.csv` after a 5-minute walk in one area gives a median within 3 FPS of 53.6.

- [ ] **Step 2: Built-in ProMotion display**

Same session via `restart.py`, window dragged to the built-in display before play; 5 minutes, same route. Record the row and whether motion looks smoother to the owner (one word: yes/no).

- [ ] **Step 3: GPU-thread knobs, 3 minutes each, same route**

`restart.py <session> --tuned --env BB_ASYNC_SUBMIT=0`, then `--env BB_VK_RECORD_THREAD=0`, then `--env BB_FRAMES_AHEAD=2`, then `--env BB_PRESENT_THREAD=0`. One row each.

- [ ] **Step 4: Shader cache on a repeat visit**

Restart twice over the same route; record `compiles` from both `stats.py` runs. Expected: the second run's count is at most a tenth of the first.

- [ ] **Step 5: Record, anchor, commit**

Add the table to `docs/runtime.md` with the conditions line (machine, display, route length), bump the header, `docseal anchor docs/runtime.md`, commit `Record launcher measurements`.
