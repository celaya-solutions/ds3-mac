```text
Document:    Dark Souls III on Mac with bbport
Version:     v1.7.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-21
SHA256:      e357904f0ed113916862c82022f6139fd666a114486098de143935061c38853e
Chain:       solana-mainnet
Tx:          ias9JN6oN7jAAfGUhgNoncJFVZmps76YPjG17hC1urGTYdZyReUuWbrivBPNvnD6qRtCcnnvrDnuHUVgUeSccjq
License:     MIT / CSR (Celaya Solutions)
```

# Dark Souls III compatibility test

[Choose a path](../README.md#choose-your-path) · [Try the code quest first](quest.md#vii--read-the-runes)

This experiment runs a local PS4 dump of Dark Souls III with the installed
macOS bbport runtime. It targets CUSA03388 version 01.00 with bbport 0.4-v1; other versions are unverified. Supply your own
game files, bbport installation, and the Bloodborne executable supported by
that installation. No games or runtime binaries are included here.

## Run

You need macOS, Python 3.9 or later, the `codesign` command, and a separately installed, trusted bbport 0.4-v1 runtime with its Python scripts and libraries. No package install in this repository supplies that runtime. You also need your own DS3 CUSA03388 v1.00 files and the Bloodborne executable supported by that runtime. If those inputs are missing, you can still run the adapter tests below.

Close other bbport sessions. From this checkout, replace all three example paths:

```sh
python3 play.py \
  --game /path/to/CUSA03388-app \
  --bbport /path/to/bbport.app/Contents/Resources/bbport \
  --reference-game /path/to/supported-Bloodborne \
  --timeout 300
```

The defaults use the existing bbport 0.4-v1 installation and merged Bloodborne
reference under `~/Documents/bloodborne`. Override them with `--bbport` and
`--reference-game` if needed. The reference executable's loaded-image hash
must match bbport's supported Bloodborne version.

Each run creates a fresh folder under `runtime/`, including a separate Mac
test app, save folder, settings, logs, and generated images.
`--data` chooses a different fresh folder. Runs stop after the chosen time
(1–600 seconds, default 120). Use `--timeout 0` to play until you quit.
Close any other bbport game before starting.
To resume a test, pass `--save-from /path/to/previous-run/user`; the launcher
copies that folder and leaves the earlier save untouched. Quit through the
game's System menu before the time limit to avoid its unclean-exit warning.
With no time limit, quit through that menu when you finish; the final report
is written after the process exits.

### Reopen a session or use a Desktop shortcut

After a session has finished and has a DS3 save, reopen it without preparing
the game again:

```sh
python3 restart.py /path/to/previous-run --fps-size 3
```

Use `--fps-size 3` only with the patched source runtime; otherwise omit it.
The shortcut installed on the local test Mac, **Dark Souls III.command** on
the Desktop, runs this command with the prepared session's paths. Double-click
it to play until you quit. Progress stays in that session's `user` folder.
Each launch first copies the saves and settings into `backups/<timestamp>`;
backup failure stops launch. Logs get separate `out/play-<timestamp>.log` files.
Duplicate launches are rejected, and changed probe/GPU binaries require a fresh
`play.py` run with `--save-from`. Older reports lack the signed app's hash;
prepare a fresh session with the current launcher before using `restart.py`.
Keep the prepared session and engine in place.

Fresh sessions default to native 1080p with MetalFX temporal anti-aliasing
(`upscaler=metalfx`, `preset=0`, "Native AA": render and output both 1080p),
object motion off, and live resolution changes off. Frame diagnostics are
disabled to avoid their counters and per-frame disk writes; add `--frame-stats`
to `play.py` for a diagnostic run. Both launchers point KosmicKrisp's shader
cache at `runtime/cache/mesa` (shared across sessions, 4 GB cap) so repeat
visits recompile less. Restarting preserves the session's saved settings. The
engine's shadow, LOD, and startup resolution patches target Bloodborne and must
not be applied to DS3.

### Tuned launches, overrides, patch files, and statistics

`--tuned` applies the setup measured on October 21
([below](#measured-tuning--october-21-2026)): `BB_VBLANK_HZ=0`,
`BB_STAGING_KEEP_MB=2048`, `BB_FAULT_WINDOW=1024`, `BB_RETINA=0`. `--env
KEY=VALUE` (repeatable) sets one runtime (`BB_*`) or shader-cache (`MESA_*`)
variable; it is applied after `--tuned`, so `--tuned --env BB_VBLANK_HZ=30`
keeps the other three. The session's `bbport.ini`, Vulkan library paths, and
`VK_DRIVER_FILES` always win. Every `BB_*` variable from your shell is still
dropped. `play.py` records the list in `result.json` (`extra_env`), and
`restart.py` replays it unless you pass `--tuned` or `--env` again, so a
Desktop shortcut needs no new flags.

`--patches FILE` copies a BBPATCH2 file you built yourself (bbport's
`scripts/patches.py` format) into the session's `out/patches.bin`, passes it to
the probe, and records its hash; `restart.py` passes it again and refuses to
start if the file changed. This repository never builds or bundles patch files.

`python3 stats.py <session>/out/frames.csv` summarizes a frame CSV from a
`--frame-stats` run: gameplay rows only (`--min-draws`, default 500), median,
p10 and p1 FPS, frames over `--hitch-ms` (default 50), median write-fault
milliseconds, shader compiles, and image upload megabytes; `--json` for
machines. The October 21 rows in this guide reproduce from it to one decimal.

Keyboard controls: Space confirms; I/J/K/L move through menus; Return is
Options and skips the opening movie. WASD moves, arrows turn the camera,
3 attacks, and left Shift rolls. Hold a key briefly so the game sees it.

## Use the local Bloodborne runtime improvements

Both runtime layouts render through KosmicKrisp, which translates Vulkan to
Apple Metal. The runtime and original game code are x86-64 and use Rosetta 2;
this is not an ARM-native game port.

`--bbport-src` selects an already-built bbport 0.4-v1 checkout instead of the
packaged runtime. It needs `out/bb-probe`, `out/gpu/libbbgpu.dylib`, the Python
scripts, and the standard `deps-x86_64/lib` dependencies, including KosmicKrisp.
Build that trusted checkout with its own `tools/macos/setup_deps.sh` and
`tools/macos/build.sh` first if needed. Do not pass both `--bbport` and
`--bbport-src`. The packaged runtime remains the default.

```sh
python3 play.py \
  --game /path/to/CUSA03388-app \
  --bbport-src ~/Documents/bbport-mac \
  --reference-game /path/to/supported-Bloodborne \
  --save-from /path/to/previous-run/user \
  --fps-size 3 --timeout 0
```

The reviewed local Bloodborne build adds two optional renderer patches:
`vertex-format-standin.patch` replaces an unsupported vertex format with a
32-bit stand-in, and `big-fps-counter.patch` enables `--fps-size 1` through `6`.
They live in the Bloodborne project's `patches/bbport/` directory and retain
their GPL-2.0-or-later terms. The source option uses the build you supply; it
does not apply or build those patches. Omit `--fps-size` if your build lacks
the counter patch. A stand-in can avoid a crash while rendering an incorrect
draw; using it does not prove DS3 needs it or that a scene renders correctly.

The launcher copies only the probe into its separate app and links to that
build's GPU library and dependencies. It records the probe and GPU hashes in
`out/result.json` when the session ends, including a separate hash for the
signed app's probe. It does not modify the source build,
the earlier save, or Bloodborne settings. Bloodborne's executable-address,
resolution, and frame-rate patches are not compatible evidence for DS3 and
are never passed to this launcher.

## What the adapter fixes

Stock bbport rejects DS3. Skipping the title check alone stops during libc
startup at `959qrazPIrg#s#J`, the import for `sceKernelGetProcParam`.
Bloodborne calls the same function using `959qrazPIrg#p#J`.

Library IDs are local to each executable. The adapter reads the library and
module names **and versions** from both executables, then translates the
generated linked image's import names to bbport's expected IDs. It changed
455 imports in this dump. Unknown identities remain unsupported; they do
not silently bind to an unrelated Bloodborne function.

Only import-name slots in a separate generated image change. Source game
files stay intact. The launcher applies no Bloodborne address patches or
frame-rate patches. It leaves bbport's Bloodborne settings and saves alone.
The installed GPU library still uses its shared shadPS4 cache location,
with the DS3 title ID; cache isolation is not complete.

## Checks

```sh
python3 -m unittest -v
git diff --check
```

The tests cover the observed startup failure, library-ID collisions, version
mismatches, unknown IDs, and preservation of all linked-image bytes outside
the import names. Launcher tests also cover both runtime layouts, matching
Metal library paths, copied saves, rejected inputs, FPS scaling, watchdogs,
`--tuned`/`--env` precedence, and patch files. Restart tests cover save
backups, repeated progress, separate logs, disabled diagnostics, concurrent
launches, changed runtimes, replayed overrides, changed patch files, and backup
failures. `stats.py` has its own tests.
Runtime logs and saves are ignored by Git.

## Source-build startup check — October 21, 2026

The local bbport 0.4-v1 build with both patches remapped the same 455 imports,
initialized KosmicKrisp, and displayed the opening logo with the enlarged FPS
counter. The 20-second startup check ended at its configured watchdog
(exit 142). This verifies startup and the overlay, not gameplay performance
or the vertex fallback. Private logs and the runtime hashes are in
`runtime/metal-smoke-20261021/out/` on the test machine.

## Measured tuning — October 21, 2026

Conditions: MacBook Pro M5 Max (18 cores, 128 GB), macOS 27.0, bbport 0.4-v1
source build (`--bbport-src`) under Rosetta 2 with KosmicKrisp, game window on
an external 1920×1080 60 Hz monitor, `BB_FRAME_STATS=1` with the frame CSV,
the frame-limiter code patch below, vblank unpaced (`BB_VBLANK_HZ=0`). Each
row is one short play stretch, gameplay frames only (draw count above 500).

| Setup | Play | Median FPS | p10 FPS | p1 FPS | Frames over 50 ms | Write faults ms/frame |
| --- | --- | --- | --- | --- | --- | --- |
| Native 2560×1440 patch, MetalFX, defaults | 20 min | 39.5 | 28.7 | 15.6 | 845 | 15.1 |
| 1080p + `BB_STAGING_KEEP_MB=2048` + `BB_FAULT_WINDOW=1024` | 3 min | 53.6 | 42.0 | 28.2 | 13 | 11.8 |
| Same + `BB_GPU_QOS=1` + macOS full screen (Game Mode tag) | 3 min | 48.2 | 33.6 | 23.9 | 12 | 22.3 |

What the counters said: the emulator's GPU command thread was 98–100% busy
and the game threads spent 12–22 ms per frame in write-fault handling, while
the GPU itself was 24–47% busy. Rendering 1440p for a 1080p monitor was wasted
work but not the limit. Stalls of 270–440 ms were texture streaming uploads of
15–16 MB, with a few shader compiles up to 2.9 s. A larger staging pool and a
wider fault window removed most of them. Interactive thread priority plus full
screen doubled the write-fault time and was reverted; those two changes were
not separated and the play areas differed, so that comparison is indicative
only.

Code patches, compiled with the bbport patch tools into a `--patches` file,
offsets for CUSA03388 v1.00 only: at `0x18314b0` the bytes `41 0f 46 c6`
become `90 90 90 90` (frame limiter test). The 1440p row also changed
`80 07 00 00 38 04 00 00` at `0x5ac2ffc` to `00 0a 00 00 a0 05 00 00`
(render size 1920×1080 to 2560×1440).

At the time, `play.py` and `restart.py` replaced every `BB_*` variable with
their own, so this setup was launched by hand from a prepared session folder,
with `bbport.ini` set to `output_res=1920x1080`, `upscaler=metalfx`,
`show_fps=1`, from the bbport checkout as the working directory. The launchers
now reproduce it with `--tuned --patches <your file>`
([above](#tuned-launches-overrides-patch-files-and-statistics)). The hand
launch stays here as the record of what was measured.

```sh
D=/path/to/session L=~/Documents/bbport-mac/deps-x86_64/lib
BB_CONFIG=$D/bbport.ini BB_FULLSCREEN=0 BB_RETINA=0 BB_OBJECT_MOTION=0 \
BB_VBLANK_HZ=0 BB_FPS_SCALE=3 BB_STAGING_KEEP_MB=2048 BB_FAULT_WINDOW=1024 \
BB_VULKAN_LIBRARY=$L/libvulkan.1.dylib SDL_VULKAN_LIBRARY=$L/libvulkan.1.dylib \
VK_DRIVER_FILES=$L/kosmickrisp/kosmickrisp_mesa_icd.json \
"$D/DS3 Test.app/Contents/MacOS/bb-probe" $D/out/boot-ds3.bin \
  --content-profile $D/out/content.bin --app0 /path/to/CUSA03388-app \
  --user $D/user --patches $D/out/performance-1080p.bin --timeout 0
```

Private CSVs, logs, and patch files are in `runtime/goal-native-1440p/out/`
on the test machine; they are not distributed.

## Recorded observations — October 16, 2026

These observations come from the original local compatibility run. Publishing this guide did not rerun the game. The private screenshots and saves are not distributed in the repository.

With the adapter, the installed 0.4-v1 runtime reached the title screen,
created a fresh save, played the opening movie, and rendered the character
creator. A new Knight reached the Cemetery of Ash. Walking and a sword swing
worked, with the overlay near 30 FPS. The first visible test ended at its
configured 300-second watchdog. This is an early compatibility result, not
a full-game or sustained-performance claim. Sound quality has not been
checked by listening.

Local evidence is in `runtime/visual2/`: title and gameplay screenshots,
stdout/stderr logs, frame CSV, and the test save. Earlier failures are in
`runtime/baseline/` and `runtime/probe/`. `runtime/final-check/` exercises the
finished launcher with a copy of that save.

bbport and its bundled components retain their own licenses. This repository
contains only the local adapter, test launcher, tests, and notes.
