```text
Document:    Dark Souls III on Mac — Agent Notes
Version:     v1.2.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-21
SHA256:      bdf4fa44ef2d04499b1fc9b58dc91ea0e6994982f22f0403e13ea2fa555dc2db
Chain:       solana-mainnet
Tx:          rC3uaDCPDnBqKVnac6yUkiZCfn25DJCJZdcsaEHYZqtp5TrQFUbaeUZsdA4HBCsCMYJ7nYqrncbPM6BL1ALb9wC
License:     MIT / CSR (Celaya Solutions)
```

# Working rules

Use isolated worktrees. Commit completed work; merge or publish only when directly requested. Never use GitHub Actions. Use graft before locating or understanding code; indexing is local and regenerable.

Keep games, runtimes, generated images, keys, saves, raw logs, and private backups out of Git. Preserve the Bloodborne project and its dirty worktrees. Do not inspect or modify excluded drives. Keep the PS4 offline and its firmware unchanged.

Keep the regular, quest, and cliff-notes learning paths consistent. Quest hints and answers use closed details blocks. Prerequisites, safety, and recovery remain visible. Companion prompts ask missing questions and wait for required console observations.

Use the standard document header. Anchor changed header-bearing files before commits; stamp and record the reason if anchoring fails. Never invent hashes or transactions. All original code, tests, documentation, and prompts use MIT, with copyright attribution to CSR (Celaya Solutions). Use `License:     MIT / CSR (Celaya Solutions)` in document headers; the owner explicitly replaced the prior rights-reserved and split-license terms. Preserve third-party credits and terms.

## Code and evidence

The adapter targets CUSA03388 01.00 and bbport 0.4-v1. Library IDs are executable-local: match library/module names and versions. Do not strip IDs, bind unrelated libraries, or apply Bloodborne address patches to DS3.

Run `python3 -m unittest -v` and `git diff --check` locally. The six tests cover import identity, collisions, versions, unknown IDs, and preservation of image bytes outside import names.

The original attended test reached Cemetery of Ash with walking and sword input near 30 FPS. Private evidence lives in the test worktree’s ignored runtime folders; it is not bundled. Publishing documentation does not repeat that run. Full-game coverage, sustained combat performance, controller input, and listened-to audio remain unverified. The GPU cache still uses the shared shadPS4 root under the DS3 title ID. Test apps share a bundle ID; use their full path when controlling multiple copies. Copy prior test saves with `--save-from`; do not modify the only save.

## Release notes

2026-10-16: The owner approved merging and publishing main to celaya-solutions/ds3-mac and requested a profile pin. Combined the completed adapter with three learning paths, added explicit runtime requirements and licenses, and checked the six local tests. The reported 1.7 million Bloodborne views is an owner-supplied launch figure, not an independently measured project result.

No Bloodborne project URL has been confirmed; add it when supplied. Keep future runtime claims tied to observed test conditions.

2026-10-16 completion: Integrated the adapter and public guides; all six tests, document links, closed disclosures, and header hashes passed local checks. Profile pinning could not run because the browser connection list was empty; use GitHub’s Customize your pins control.

2026-10-16: Unified all original code, docs, and prompts under standard MIT with CSR (Celaya Solutions) copyright credit. Updated every document license header and removed split-license terms; all six tests and license-consistency checks passed.

2026-10-21: Measured tuning recorded in the README and runtime guide: 1080p with `BB_STAGING_KEEP_MB=2048` and `BB_FAULT_WINDOW=1024`, vblank unpaced, played at a median 53.6 FPS on an M5 Max over one short session in one area. Thread priority plus full screen hurt and were reverted. The launchers still strip `BB_*` variables, so that setup is a hand launch; keep the numbers tied to those conditions.

2026-10-21 night: Launcher knobs shipped: `--tuned`, `--env`, `--patches`, `stats.py`, MetalFX Native AA default, Mesa cache pin; twenty-four tests. Engine work in the local bbport checkout, exported as three patches beside the Bloodborne project's: macOS host-import probe (import works, 6x faster GPU reads), guest memory in place through host-pointer import (`BB_GUEST_IN_PLACE=1` crashes DS3 in bbport's in-place command-write path unless `BB_GPU_COMMAND_WRITES=0`; unmeasured in play), and MetalFX frame interpolation (`BB_METALFX_INTERPOLATE=1`, smoke-clean, never seen in gameplay). Both engine flags stay off; the play rows are the owner's. Specs and plans under `docs/superpowers/`.
