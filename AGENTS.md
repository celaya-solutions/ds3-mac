```text
Document:    Dark Souls III Public Preparation — Agent Notes
Version:     v1.0.1
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      8be976d2faf478ebb29cf9b2be0f9b6929920d0c9d3094dda329eda54cdca8c2
Chain:       solana-mainnet
Tx:          4ZXoatxDpTCXJCH5ypa9RSggRS6HpmRw81akAmkYL1zbJZea6nvXK4iQFT4M3mHNeF198U5AioXXwQk2Rycnr1pA
License:     All Rights Reserved / Celaya Solutions
```

# Scope and working rules

Use isolated worktrees. Commit completed work. Do not merge without a direct request. Never use GitHub Actions for checks, builds, releases, or deployment.

Use graft first when locating or understanding code. This branch currently contains documentation only. Keep private game files, keys, saves, backups, and raw runtime logs out of Git. Do not change PS4 firmware or connect it to the internet. Do not touch excluded drives.

Keep three paths: regular tutorial, quest, and cliff notes. Quest hints and answers use closed HTML details blocks. Safety, prerequisites, device steps, and failed-check handling stay visible. All paths use the same factual workflow. Prompts ask missing setup questions and wait for required device observations.

Use the standard header for documents. Anchor changed header-bearing files before committing; stamp and record the reason if anchoring fails. Do not fabricate transactions or hashes.

## Public release gates

- Confirm the intended scope with the owner: full backup-to-code journey or adapter-focused entry point. The neighboring adapter worktree is unfinished and must not be copied or published without coordination.
- Select an explicit code and documentation license. Current document headers retain the required rights notice; no broad reuse grant has been chosen.
- Confirm the Bloodborne project link and any public launch claim. The owner reported 1.7 million views; that figure is not independently verified and has not been added to public copy.
- Confirm the GitHub destination and publishing authorization. No remote was configured at preparation start; do not assume an inaccessible repository name is available.
- Review all intended code, dependency licenses, binaries, history, and runtime claims before publishing a combined repository. Documentation checks alone do not validate the adapter.

## Handoff

The regular guide was carried from the committed offline-backup-guide branch. Its recorded results are inherited observations, not a new device run. The public-prep branch leaves main and neighboring worktrees untouched.

## Completion note

2026-10-16: Prepared the README, regular guide, six-stage quest, cliff notes, companion prompt, and contribution notes. Local link, HTML disclosure, private-data pattern, whitespace, and document-hash checks passed; no device or runtime test was performed.
