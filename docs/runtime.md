```text
Document:    Dark Souls III on Mac with bbport
Version:     v1.5.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-21
SHA256:      dee7b20c383b8d9f9c51e72784a33ec2de0f229677c75274d4cad5ec9f01f4eb
Chain:       solana-mainnet
Tx:          5LxG6afRvgoDixtPcZ2nQdvqdndmqkw3VnDaJEtKisXfxNrt2KmFbzhYhGKLewapyz9oFpvob9U82QFxvBLj8N34
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
`play.py` run with `--save-from`. Keep the prepared session and engine in place.

Fresh sessions default to native 1080p, upscaling off, object motion off, and
live resolution changes off. Frame diagnostics are disabled to avoid their
counters and per-frame disk writes; add `--frame-stats` to `play.py` for a
diagnostic run. The shader cache remains enabled. Restarting preserves the
session's saved settings. These are conservative low-overhead defaults, not
a measured fastest preset. The engine's shadow, LOD, and startup resolution
patches target Bloodborne and must not be applied to DS3.

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
`out/result.json` when the session ends. It does not modify the source build,
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
Metal library paths, copied saves, rejected inputs, FPS scaling, and watchdogs.
Restart tests cover save backups, repeated progress, separate logs, disabled
diagnostics, concurrent launches, changed runtimes, and backup failures.
Runtime logs and saves are ignored by Git.

## Source-build startup check — October 21, 2026

The local bbport 0.4-v1 build with both patches remapped the same 455 imports,
initialized KosmicKrisp, and displayed the opening logo with the enlarged FPS
counter. The 20-second startup check ended at its configured watchdog
(exit 142). This verifies startup and the overlay, not gameplay performance
or the vertex fallback. Private logs and the runtime hashes are in
`runtime/metal-smoke-20261021/out/` on the test machine.

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
