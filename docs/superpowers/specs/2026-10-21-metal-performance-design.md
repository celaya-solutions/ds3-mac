```text
Document:    DS3 on Mac — Metal Performance and Quality Design
Version:     v1.0.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-21
SHA256:      2f213e00483676a819c4ac3a569c3cda80c6f2277044de644b5520af495bdd75
Chain:       solana-mainnet
Tx:          3sYGpit2pMEKeaMG3RVpFZLGxMQwX5dpYfi4bmp1TkMydyPFyjXvnig6WoMjyrcqchtMkDXKRP6G6FYDhaiHBhc8
License:     MIT / CSR (Celaya Solutions)
```

# DS3 on Mac: Metal performance and quality design

## Intent

Make the measured October 21 setup reproducible from the launchers, use the idle GPU for image quality, and attack the CPU-side cost that caps frame rate. The owner skipped the design conversation; every choice below is the builder's call unless marked measured.

## What is measured (October 21, M5 Max, gameplay rows, medians)

| Run | frame ms | write_fault ms | tick_wait ms | compiles |
| --- | --- | --- | --- | --- |
| 1440p patch, 20 min | 25.3 | 15.1 | 11.7 | 165 |
| 1080p tuned, 3 min | 18.7 | 11.8 | 9.6 | 0 |
| 1080p tuned, 10 min | 20.3 | 19.9 | 13.3 | 2 |

Write-fault handling on the game threads costs most of a frame. The GPU sat at 24–47% busy. Source: `runtime/goal-native-1440p/out/frames-*.csv` (private) and `docs/runtime.md`.

Facts checked on this machine on October 21:

- This repo has no Metal code. Rendering goes game → Rosetta 2 → bbport (shadPS4 video core, Vulkan) → KosmicKrisp (Mesa Vulkan on Metal).
- KosmicKrisp on the M5 Max advertises `VK_EXT_external_memory_host`, `VK_EXT_external_memory_metal`, `VK_EXT_host_image_copy`, `VK_KHR_present_wait`. Probe source: `runtime/probe-ext/ext.c` (private).
- bbport's guest-in-place memory model is stubbed off on macOS (`gpu/shim/bbport_guest_memory.cpp`, the `__APPLE__` branch). The Linux path exports dma-bufs; macOS guest memory is one POSIX shared memory object with an unprotected backing view (`src/runtime_memory.c`, `backing_base`, 256 MiB chunks).
- bbport already drives `MTLFXTemporalScaler` through heaps exported with `VK_EXT_external_memory_metal` (`gpu/shim/bbport_metalfx.mm`, `vk_metalfx.cpp`). No frame interpolator is wired. The macOS 27 SDK ships `MTLFXFrameInterpolator` (macOS 26+), chainable to a temporal scaler.
- KosmicKrisp honors `MESA_SHADER_CACHE_DIR` and `MESA_SHADER_CACHE_MAX_SIZE`; `~/.cache/mesa_shader_cache` is already in use (42 MB). bbport's own `.spv` cache lives under `~/Library/Application Support/shadPS4/cache/CUSA03388`.
- `play.py` and `restart.py` strip every `BB_*` variable and pin `BB_VBLANK_HZ=60`; the tuned launch was done by hand.

## Goals

1. One command (and the Desktop shortcut) launches the measured tuned setup, including a patch file the owner supplies.
2. Frame statistics come from a checked-in script, not a scratchpad.
3. MetalFX temporal anti-aliasing is the default image path at 1080p output.
4. The engine can use guest memory in place on Apple silicon, removing write-fault tracking.
5. MetalFX frame interpolation can double presented frames when the CPU is the limit.
6. Each change ships with a measured before/after row in `docs/runtime.md`.

## Non-goals

- A native arm64 build of the GPU library (Rosetta is per process).
- Replacing KosmicKrisp or writing a Metal renderer.
- Changing the game's own code beyond the patch file the owner already uses (see `docs/runtime.md`, measured tuning). This repo never builds or bundles such patches.
- Game Mode, `BB_GPU_QOS`, or full screen (measured worse).

## Anti-goals

- A launcher default that differs from what was measured.
- Silent fallback: if guest-in-place or interpolation cannot run, the log must say so in one line and the session must still play.
- Any Bloodborne address, resolution, or frame-rate patch reaching DS3.

## Constraints

- Python 3.9+, standard library only, macOS. Tests: `python3 -m unittest -v`, `git diff --check`.
- Engine work lands in the local bbport-mac checkout (branch `csr/surface-format-fallback`, never pushed) and is exported as `.patch` files beside the two existing ones in the Bloodborne project's `patches/bbport/`, GPL-2.0-or-later. This repo only documents how to apply them.
- Engine build: `tools/macos/build.sh` (x86-64 under Rosetta). C++ tests: `ninja -C out/gpu settings-test upscaler-support-test` then run the binaries. Python tests: `python3 -m unittest discover -s tests`.
- Standard document header on every new document; anchor with docseal before commit.
- Play sessions never touch the only save: `restart.py` backs up first; new sessions use `--save-from`.

## Decisions (builder's calls)

- Launcher knobs: `--env KEY=VALUE` (repeatable, `BB_*` and `MESA_*` only) and `--tuned` = `BB_VBLANK_HZ=0 BB_STAGING_KEEP_MB=2048 BB_FAULT_WINDOW=1024 BB_RETINA=0`. Explicit `--env` wins over `--tuned`.
- Shader cache: both launchers set `MESA_SHADER_CACHE_DIR` to `runtime/cache/mesa` (shared across sessions, gitignored) and `MESA_SHADER_CACHE_MAX_SIZE=4G`.
- Patch file: `--patches FILE` copies the file into the session's `out/patches.bin`, passes `--patches` to the probe, and records its hash in `result.json`. `restart.py` passes it when present.
- Default `bbport.ini`: `upscaler=metalfx`, `preset=0` (Native AA), `sharpen=0`.
- Guest-in-place on macOS imports the runtime's backing view per 256 MiB chunk with host-pointer import; the runtime keeps mapping from its shared memory object. Gate: `BB_GUEST_IN_PLACE=1`, off by default until measured.
- Frame interpolation: `BB_METALFX_INTERPOLATE=1`, off by default; the interpolator chains to the existing temporal scaler; the presenter shows the interpolated frame then the real one, half a measured frame interval apart.

## Left to the builder

Exact Objective-C++ structure of the interpolator, pacing clock source in the presenter, and how the probe reports alignment. The plans name files, signatures, and tests.
