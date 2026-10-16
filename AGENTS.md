```text
Document:    Dark Souls III Mac Agent Notes
Version:     v1.0.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      9b8a5f59271998a2e47ef49a7a9e60d82fb24a748af47bd0a4afde874c5086ed
Chain:       solana-mainnet
Tx:          5KSuzmeakeo5uKZp7NcjGDWWegp6zpdGDrqSRZzSW6riYGn3QpmTRqK3MQ4HVqKr6FAmg27fSujRxN39z5T6GdVz
License:     All Rights Reserved / Celaya Solutions
```

Work in isolated worktrees. Do not merge or push without a direct request.
Run checks locally; never use GitHub Actions. Keep games, runtimes, generated
images, logs, and saves out of Git. Preserve the Bloodborne project and its
dirty source checkout. Do not inspect or modify the external SSD.

The source bug is executable-local library IDs: DS3 uses `#s#J` for kernel
imports; Bloodborne uses `#p#J`. Match both library/module names and versions.
Do not strip IDs or apply Bloodborne offsets to DS3. The adapter currently
targets only CUSA03388 01.00 and the installed bbport 0.4-v1 contracts.

Validation: `python3 -m unittest -v` and `git diff --check`. Six focused tests
pass. The attended run reached Cemetery of Ash, with walking and a sword
swing near 30 FPS. Evidence and saves are under ignored `runtime/visual2/`.
Use `--save-from` to copy a prior test save, not the only original save.

Limits: full-game coverage, sustained combat performance, controller input,
and listened-to audio are unverified. GPU cache still uses shadPS4's shared
cache root under the DS3 title ID. Test apps share a bundle ID; use their full
app path with computer-use tools when multiple copies are registered.

2026-10-16 completion: Committed the isolated launcher and import adapter.
The final launcher reloaded a copied save; movement, camera, and attacks worked in Cemetery of Ash.
