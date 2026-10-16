```text
Document:    Dark Souls III on Mac — Agent Notes
Version:     v1.0.1
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      ea8f99b071b1c58f02652888e71a4c20e26ae174d6bbda9096b623e387b3ed0d
Chain:       solana-mainnet
Tx:          46KdStPKcFXZHhmjTp5z4cLzf2u21SMDDiCikhuj857xgjsYaCLmrZfwp5sgtTvVup28xVZZmYwiVJ35k9Dah2CT
License:     All Rights Reserved / Celaya Solutions
```

# Working rules

Use isolated worktrees. Commit completed work; merge or publish only when directly requested. Never use GitHub Actions. Use graft before locating or understanding code; indexing is local and regenerable.

Keep games, runtimes, generated images, keys, saves, raw logs, and private backups out of Git. Preserve the Bloodborne project and its dirty worktrees. Do not inspect or modify excluded drives. Keep the PS4 offline and its firmware unchanged.

Keep the regular, quest, and cliff-notes learning paths consistent. Quest hints and answers use closed details blocks. Prerequisites, safety, and recovery remain visible. Companion prompts ask missing questions and wait for required console observations.

Use the standard document header. Anchor changed header-bearing files before commits; stamp and record the reason if anchoring fails. Never invent hashes or transactions. Original Python code is MIT; original Markdown documentation is CC BY 4.0. Preserve third-party credits and terms.

## Code and evidence

The adapter targets CUSA03388 01.00 and bbport 0.4-v1. Library IDs are executable-local: match library/module names and versions. Do not strip IDs, bind unrelated libraries, or apply Bloodborne address patches to DS3.

Run `python3 -m unittest -v` and `git diff --check` locally. The six tests cover import identity, collisions, versions, unknown IDs, and preservation of image bytes outside import names.

The original attended test reached Cemetery of Ash with walking and sword input near 30 FPS. Private evidence lives in the test worktree’s ignored runtime folders; it is not bundled. Publishing documentation does not repeat that run. Full-game coverage, sustained combat performance, controller input, and listened-to audio remain unverified. The GPU cache still uses the shared shadPS4 root under the DS3 title ID. Test apps share a bundle ID; use their full path when controlling multiple copies. Copy prior test saves with `--save-from`; do not modify the only save.

## Release notes

2026-10-16: The owner approved merging and publishing main to celaya-solutions/ds3-mac and requested a profile pin. Combined the completed adapter with three learning paths, added explicit runtime requirements and licenses, and checked the six local tests. The reported 1.7 million Bloodborne views is an owner-supplied launch figure, not an independently measured project result.

No Bloodborne project URL has been confirmed; add it when supplied. Keep future runtime claims tied to observed test conditions.

2026-10-16 completion: Integrated the adapter and public guides; all six tests, document links, closed disclosures, and header hashes passed local checks. Profile pinning could not run because the browser connection list was empty; use GitHub’s Customize your pins control.
