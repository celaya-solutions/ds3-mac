```text
Document:    Dark Souls III on Mac with bbport
Version:     v1.2.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      675db45d04cbd1fd4300cd1f77390db5ced04386fe5fc1aaca92ca6254207a97
Chain:       solana-mainnet
Tx:          VAEf5y4vjmQnBmdzM2zzTh9CiCwpFAoUT6YRMrJHcCVXZ2nronqPsAteps58mMnEEeDV6DB7d31SsDC5s4wV47f
License:     All Rights Reserved / Celaya Solutions
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
test app, save folder, settings, logs, frame data, and generated images.
`--data` chooses a different fresh folder. Runs stop after the chosen time
(1–600 seconds). Close any other bbport game before starting.
To resume a test, pass `--save-from /path/to/previous-run/user`; the launcher
copies that folder and leaves the earlier save untouched. Quit through the
game's System menu before the time limit to avoid its unclean-exit warning.

Keyboard controls: Space confirms; I/J/K/L move through menus; Return is
Options and skips the opening movie. WASD moves, arrows turn the camera,
3 attacks, and left Shift rolls. Hold a key briefly so the game sees it.

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
the import names. Runtime logs and saves are ignored by Git.

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
