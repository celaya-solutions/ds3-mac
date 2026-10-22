```text
Document:    DS3 on Mac — Engine Metal Implementation Plan
Version:     v1.0.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-21
SHA256:      4844fcc87d50de4d0c2487f0a842ebccc3c1392d3a46e07b78b0a412e2ff3ccd
Chain:       solana-mainnet
Tx:          4rVci5gkR1tsX2PLKP71C2ni6HBRjh9crLnzV3CAmSEL7CmF4sxv9qFBFM2uQSRZMmpLEVKEK1YsStP7hqrzC2qQ
License:     MIT / CSR (Celaya Solutions)
```

# Engine Metal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** bbport on Apple silicon reads guest memory in place (no write-fault tracking) and can present MetalFX-interpolated frames between rendered ones.

**Architecture:** The Linux guest-in-place path exports Vulkan memory as dma-bufs for the runtime to map. macOS inverts it: the runtime keeps its POSIX shared-memory pool, and the GPU library imports the pool's unprotected backing view per 256 MiB chunk with `VK_EXT_external_memory_host`, so the existing arena binding and `BbGuestMemory::Find` work unchanged. Frame interpolation reuses the MetalFX bridge (exported heaps, shared events) and adds one presenter pacing rule.

**Tech Stack:** C++20 / Objective-C++, Vulkan 1.4 on KosmicKrisp, Metal / MetalFX (macOS 26+ APIs on macOS 27), CMake + Ninja, x86-64 under Rosetta 2.

**Spec:** `~/Documents/ds3-mac/docs/superpowers/specs/2026-10-21-metal-performance-design.md`

## Global Constraints

- Work in `~/Documents/bbport-mac` on branch `csr/surface-format-fallback`; never push. After each task, `git diff <base>..HEAD -- <files> > ~/Documents/bloodborne/patches/bbport/<name>.patch` and commit that file in the Bloodborne project (GPL-2.0-or-later, keep the existing LICENSE beside it).
- Build: `tools/macos/build.sh`. Tests: `ninja -C out/gpu settings-test upscaler-support-test && out/gpu/settings-test && out/gpu/upscaler-support-test`; `python3 -m unittest discover -s tests`.
- Every new behavior is off by default and gated by one environment variable; when it cannot run, one `printf` line says why and the session continues as before.
- Nothing from the Bloodborne address, resolution or frame-rate patches is applied to DS3.
- Play checks use `~/Documents/ds3-mac` Plan A tooling: `play.py --bbport-src ~/Documents/bbport-mac --save-from <prior>/user --tuned --frame-stats --env <gate>=1`, then `stats.py`.

## Review Focus

- The import alignment reported by the driver is larger than the runtime's chunk start alignment: `AllocChunk` must round the pointer down and the size up, or refuse the chunk (Task 2 self-test).
- A chunk the driver refuses to import: the runtime keeps it in shared memory and the GPU copies it as before; the log names the chunk (Task 2 self-test, forced by `BB_GUEST_IMPORT_FAIL_AT=<phys>`).
- Write tracking off with guest-in-place: data the game writes without an announcement reaches the GPU late. `BB_WRITE_TRACKING=1` must restore page protection while memory stays in place (Task 2 play check, second row).
- Frame interpolation when the render size changes mid-session (menu): `Interpolate` returns false until two frames at the new size exist and the interpolator is recreated with history reset (Task 3 `Interpolate` contract; owner play check through the resolution menu).
- Interpolation when a real frame arrives before the half interval elapsed: the pending interpolated frame is dropped, never shown after its successor (Task 3 test).

---

### Task 1: macOS host-import probe

**Files:**
- Modify: `tools/host_import_probe.c` (lines 1–12, 323, 415)
- Create: `~/Documents/ds3-mac/runtime/probe-ext/host-import.txt` (private output)
- Modify: `~/Documents/ds3-mac/docs/runtime.md` (one paragraph)

**Interfaces:**
- Produces: the probe builds on macOS: `#ifdef __APPLE__` replaces each `memfd_create` with `shm_open` of a per-pid name followed by `shm_unlink`, drops `_GNU_SOURCE` and `MFD_CLOEXEC` there; everything else unchanged.
- Produces: numbers for Task 2: `minImportedHostPointerAlignment`, import success, GPU read speed of imported memory versus the staging path, and whether CPU writes through the second mapping are seen.

- [ ] **Step 1: Build**

```sh
cd ~/Documents/bbport-mac && source deps-x86_64/env.sh && \
clang -arch x86_64 -I deps-x86_64/include tools/host_import_probe.c -L deps-x86_64/lib -lvulkan -o out/bb-host-import-probe
```

Expected before the edit: errors naming `memfd_create`. After: a binary in `out/`.

- [ ] **Step 2: Run**

```sh
VK_DRIVER_FILES=$PWD/deps-x86_64/lib/kosmickrisp/kosmickrisp_mesa_icd.json DYLD_LIBRARY_PATH=$PWD/deps-x86_64/lib \
  out/bb-host-import-probe 512 | tee ~/Documents/ds3-mac/runtime/probe-ext/host-import.txt
```

Expected: section 1 prints the alignment; section 2 imports 512 MiB without a `CHECK` failure; section 3 reports writes seen through the other mapping. If section 2 fails, stop Plan B here and report the exact line.

- [ ] **Step 3: Record**

One paragraph in `~/Documents/ds3-mac/docs/runtime.md` under a new "Guest memory import probe — <date>" heading: alignment, GB/s imported versus staging, writes seen yes/no. Bump the header, `docseal anchor`.

- [ ] **Step 4: Commit and export**

```sh
git -C ~/Documents/bbport-mac commit -am "host_import_probe: build on macOS with POSIX shared memory"
git -C ~/Documents/bbport-mac diff HEAD~1 -- tools/host_import_probe.c > ~/Documents/bloodborne/patches/bbport/host-import-probe-macos.patch
git -C ~/Documents/bloodborne add patches/bbport/host-import-probe-macos.patch && git -C ~/Documents/bloodborne commit -m "Add the macOS host-import probe patch"
git -C ~/Documents/ds3-mac commit -am "Record the guest memory import probe"
```

---

### Task 2: Guest memory in place on Apple silicon

**Files:**
- Modify: `gpu/shim/bbport_guest_memory.cpp` (the `__APPLE__` branch, lines 13–27, becomes the implementation)
- Modify: `gpu/shim/bbport_guest_memory.h` (doc comment: dma-buf on Linux, host-pointer import on macOS)
- Modify: `src/runtime_memory.c` (new accessor), `src/runtime.h` (declaration)
- Modify: `gpu/shadps4/video_core/renderer_vulkan/vk_instance.cpp` / `vk_instance.h` (enable `VK_EXT_external_memory_host`, `IsHostImportSupported()`)
- Modify: `gpu/shadps4/video_core/buffer_cache/buffer.cpp:111-113` (arena handle type)
- Modify: `gpu/shadps4/video_core/buffer_cache/buffer_cache.cpp:488-491` (gate comment and condition)
- Modify: `docs/README-linux.md` or `tools/macos/README-macos.md` (one paragraph on `BB_GUEST_IN_PLACE` on macOS)

**Interfaces:**
- Consumes: Task 1's alignment.
- Produces: `extern "C" unsigned char *runtime_memory_backing_view(void)` in `runtime_memory.c`: returns `backing_base` after `pool()` succeeded, else `NULL`.
- Produces: on Apple, `BbGuestMemory::Usable(instance)` is true when `IsHostImportSupported()` and a self-test passes: import 2 MiB of a fresh `MAP_SHARED` anonymous mapping, write a marker through the mapping, copy the imported buffer to a host-visible buffer on the GPU, read the marker back. `PcModelGpu(instance)` returns `Usable(instance)` on Apple (the AMD-only gate stays on Linux).
- Produces: `Install(instance)` on Apple registers `AllocChunk` with `runtime_memory_set_guest_chunk_allocator` when `BB_GUEST_IN_PLACE=1` and `Usable`. `AllocChunk(phys, size)` imports `runtime_memory_backing_view() + phys` (rounded down to the alignment, size rounded up) with `vk::ImportMemoryHostPointerInfoEXT{eHostAllocationEXT}`, memory type from `getMemoryHostPointerPropertiesEXT`, creates the chunk `vk::Buffer` with `ExternalMemoryBufferCreateInfo{eHostAllocationEXT}` and the same usage flags as Linux, binds, inserts the `Chunk` sorted by `phys`, prints `Guest memory: direct memory %#llx+%llu MiB imported in place (host pointer), %llu MiB so far`, and returns `-1` so the runtime keeps mapping the chunk from its shared memory object (same pages). On failure it prints `Guest memory: import of chunk %#llx failed (%s); the GPU copies it` and returns `-1`.
- Produces: `buffer.cpp` arena `ExternalMemoryBufferCreateInfo.handleTypes` is `eHostAllocationEXT` on Apple, `eDmaBufEXT` elsewhere.
- Produces: test hook `BB_GUEST_IMPORT_FAIL_AT=<hex phys>` makes `AllocChunk` take the failure path for that chunk (Review Focus).

- [ ] **Step 1: Write the failing self-test**

Add to `tests/test_upscaler_support.cpp`'s pattern a new `tests/test_guest_memory_mac.cpp` (CMake target `guest-memory-test`, `EXCLUDE_FROM_ALL`, links `shim/bbport_guest_memory.cpp` and the runtime stubs): creates an instance on the default device, asserts `BbGuestMemory::Usable(instance)` is true, calls `AllocChunk`-equivalent through `Install` with a fake runtime backing view of 2 chunks, asserts `Find(0)` and `Find(256 << 20)` return chunks with `memory` set, and with `BB_GUEST_IMPORT_FAIL_AT=0x10000000` asserts `Find(256 << 20)` is null and `Find(0)` is not.

- [ ] **Step 2: Run to verify it fails**

Run: `ninja -C out/gpu guest-memory-test && out/gpu/guest-memory-test`
Expected: link or assertion failure (`Usable` is false on the stub).

- [ ] **Step 3: Implement**

The Apple branch mirrors the Linux `AllocChunk`/`Usable`/`Install` structure with import in place of export; `Find` is shared code (move it out of the `#else`). Extension enablement in `vk_instance.cpp` follows how `VK_EXT_external_memory_metal` is enabled there.

- [ ] **Step 4: Run tests and build**

Run: `tools/macos/build.sh && ninja -C out/gpu guest-memory-test settings-test && out/gpu/guest-memory-test && out/gpu/settings-test && python3 -m unittest discover -s tests`
Expected: PASS.

- [ ] **Step 5: Play check (owner), three rows**

Fresh `play.py` session as in Global Constraints, 5 minutes on the recorded route each:
1. `--env BB_GUEST_IN_PLACE=1`: log shows `imported in place` lines and no `the GPU copies it`; `stats.py` `write_fault_ms` median under 1.0; zero `STOP:`/`Guest fault` lines in `result.json`; the owner reports no visible corruption (one word).
2. `--env BB_GUEST_IN_PLACE=1 --env BB_WRITE_TRACKING=1`: runs; row recorded.
3. Baseline `--tuned` only: row recorded the same day.
Record in `~/Documents/ds3-mac/docs/runtime.md` ("Guest memory in place — <date>"), anchor, commit.

- [ ] **Step 6: Commit and export**

```sh
git -C ~/Documents/bbport-mac add -A gpu/shim/bbport_guest_memory.cpp gpu/shim/bbport_guest_memory.h src/runtime_memory.c src/runtime.h gpu/shadps4/video_core/renderer_vulkan/vk_instance.cpp gpu/shadps4/video_core/renderer_vulkan/vk_instance.h gpu/shadps4/video_core/buffer_cache/buffer.cpp gpu/shadps4/video_core/buffer_cache/buffer_cache.cpp tests/test_guest_memory_mac.cpp gpu/CMakeLists.txt
git -C ~/Documents/bbport-mac commit -m "Guest memory in place on macOS through host-pointer import"
git -C ~/Documents/bbport-mac diff HEAD~1 > ~/Documents/bloodborne/patches/bbport/guest-in-place-macos.patch
```

Commit the patch file in the Bloodborne project.

---

### Task 3: MetalFX frame interpolation

**Files:**
- Modify: `gpu/shim/bbport_metalfx.h` (add `InterpolatorConfig`, `InterpolatorFrame`, `class Interpolator`)
- Modify: `gpu/shim/bbport_metalfx.mm` (implementation, `NSClassFromString(@"MTLFXFrameInterpolatorDescriptor")`, weak-linked like the scaler)
- Modify: `gpu/shadps4/video_core/renderer_vulkan/vk_metalfx.h` / `vk_metalfx.cpp` (`MetalFxUpscaler::Interpolate`, second output staging, previous-output retention)
- Modify: `gpu/shadps4/video_core/renderer_vulkan/vk_temporal_upscaler.cpp` (call `Interpolate` after `Run` when enabled; `InterpolationRequested()`)
- Modify: `gpu/shadps4/video_core/renderer_vulkan/vk_presenter.cpp:549-731` (`Present` double presentation), `vk_presenter.h`
- Modify: `gpu/shadps4/core/libraries/videoout/driver.cpp:503` (frame CSV gains `presented`)
- Modify: `docs/upscaler.md` (section "MetalFX frame interpolation")
- Test: `tests/test_upscaler_support.cpp`

**Interfaces:**
- Consumes: `BbMetalFx::Scaler`, `Heaps`, `Frame` events (existing); camera FOV, near and far from `vk_camera_motion.h` (line 61).
- Produces: `bool BbMetalFx::InterpolationSupported(void* heap, std::string& reason)` (class present and `+supportsDevice:` true).
- Produces: `struct InterpolatorConfig { uint32_t in_width, in_height, out_width, out_height; ColorFormat color; bool hdr; };` input = render size (depth and motion), output = output size, `colorTextureFormat`/`outputTextureFormat` RGBA16F, `scaler` = the existing temporal scaler, `requiresPrevColorTexture = YES`.
- Produces: `struct InterpolatorHeaps { void* color; void* prev_color; void* depth; void* motion; void* output; };`
- Produces: `struct InterpolatorFrame { float delta_time, near_plane, far_plane, fov_y, aspect; float jitter_x, jitter_y, motion_scale_x, motion_scale_y; bool reset, depth_reversed; void* wait_event; uint64_t wait_value; void* signal_event; uint64_t signal_value; };`
- Produces: `class Interpolator { static std::unique_ptr<Interpolator> Create(const InterpolatorConfig&, const InterpolatorHeaps&, Scaler& chained, std::string& error); bool Encode(const InterpolatorFrame&, std::string& error); bool TakeError(std::string&); };`
- Produces: `bool MetalFxUpscaler::Interpolate(const Frame& current, vk::Image interpolated)`: runs after `Run` succeeded for two consecutive frames at the same sizes; keeps the previous output staging alive one extra frame; writes the midpoint frame into `interpolated` (RGBA16F, output size, General layout afterwards). Returns false (and logs once) when sizes changed, on the first frame after a reset, or on error.
- Produces: `bool Vulkan::InterpolationRequested()`: `BB_METALFX_INTERPOLATE` is `1` and `BbSettings::Get().upscaler == UpscalerMetalFx`.
- Produces: presenter: `Presenter::Present` receives `frame->interpolated` (nullable). When set, present it first, then wait until `last_real_present + interval / 2` where `interval` is an exponential average (factor 0.1) of the last real-frame deltas, then present the real frame. If the next real frame arrives before that wait ends, drop the pending interpolated frame. The log prints `Upscaler: MetalFX frame interpolation on` once, or the reason it is off.
- Produces: frame CSV column `presented` (frames shown this row: 1 or 2).

- [ ] **Step 1: Write the failing tests in `tests/test_upscaler_support.cpp`**

Three cases, in that file's style: `InterpolationRequested()` is false with the variable unset and `upscaler=metalfx`; false with `BB_METALFX_INTERPOLATE=1` and `upscaler=taa`; true with both. Plus a presenter pacing unit: a pure function `bool ShowPending(std::chrono::nanoseconds since_real, std::chrono::nanoseconds interval, bool next_real_arrived)` (new in `vk_presenter.h`) returns false when `next_real_arrived`, false before `interval / 2`, true at or after it.

- [ ] **Step 2: Run to verify they fail**

Run: `ninja -C out/gpu upscaler-support-test && out/gpu/upscaler-support-test`
Expected: compile failure (`InterpolationRequested` undeclared).

- [ ] **Step 3: Implement the Metal side, then the Vulkan side, then the presenter**

`Encode` mirrors `Scaler::Encode`: blit uploads from the heaps into private textures, set `colorTexture`, `prevColorTexture`, `depthTexture`, `motionTexture`, `outputTexture`, `deltaTime`, `nearPlane`, `farPlane`, `fieldOfView`, `aspectRatio`, `jitterOffsetX/Y`, `motionVectorScaleX/Y`, `shouldResetHistory`, `encodeToCommandBuffer:`, blit download into the output heap, shared-event waits and signals as the scaler does. `uiTexture` stays nil (HUD is already in color; note the ghosting risk in `docs/upscaler.md`).

- [ ] **Step 4: Build and test**

Run: `tools/macos/build.sh && ninja -C out/gpu upscaler-support-test settings-test && out/gpu/upscaler-support-test && out/gpu/settings-test && python3 -m unittest discover -s tests`
Expected: PASS.

- [ ] **Step 5: Play check (owner), two rows**

Fresh session with `--tuned --env BB_METALFX_INTERPOLATE=1`, 5 minutes on the recorded route: the log shows the on-line; `stats.py` gains `presented_fps` (sum of `presented` over seconds) and reports roughly twice `median_fps`; the owner reports input feel and HUD ghosting (one word each). Second row: `--tuned` only, same day. Record under "Frame interpolation — <date>" in `~/Documents/ds3-mac/docs/runtime.md`, anchor, commit. `stats.py` change: `presented_fps` is present only when the column exists (one-line addition in `summarize`, test in `test_stats.py`).

- [ ] **Step 6: Commit and export**

```sh
git -C ~/Documents/bbport-mac add gpu/shim/bbport_metalfx.h gpu/shim/bbport_metalfx.mm gpu/shadps4/video_core/renderer_vulkan/vk_metalfx.h gpu/shadps4/video_core/renderer_vulkan/vk_metalfx.cpp gpu/shadps4/video_core/renderer_vulkan/vk_temporal_upscaler.cpp gpu/shadps4/video_core/renderer_vulkan/vk_presenter.cpp gpu/shadps4/video_core/renderer_vulkan/vk_presenter.h gpu/shadps4/core/libraries/videoout/driver.cpp docs/upscaler.md tests/test_upscaler_support.cpp
git -C ~/Documents/bbport-mac commit -m "MetalFX frame interpolation behind BB_METALFX_INTERPOLATE"
git -C ~/Documents/bbport-mac diff HEAD~1 > ~/Documents/bloodborne/patches/bbport/metalfx-frame-interpolation.patch
```

Commit the patch file in the Bloodborne project, and `stats.py` + `test_stats.py` in this repo.
