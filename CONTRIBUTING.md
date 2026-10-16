```text
Document:    Contributing to Dark Souls III on Mac
Version:     v1.0.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      ad056b6019c48cceec9cdc3167f3b843c5bcaddcb1e1dc97baa0925451c4ee24
Chain:       solana-mainnet
Tx:          3PTyATdpjKyTpeNZwJzyQtnPr2k8TMEAToHCzzc2ELLi4z6KsqkK936Kb25yHQj2CcZbGfgEw82iXnbTwgYyuvDT
License:     All Rights Reserved / Celaya Solutions
```

# Leave a clearer road

Start with the [README](README.md) and choose a learning path. This branch contains documentation; it does not yet contain the DS3 adapter or a tested launch recipe.

Useful first contributions include a clearer explanation, a broken-link fix, a better hint, or a reproducible correction to a setup step.

## Send a focused change

1. Once the public repository and license are ready, fork it on GitHub. Clone your fork and create a branch or isolated worktree for your change.
2. Keep the change small. Preserve all three learning paths. Hide optional explanations behind closed `<details>` blocks in quest mode; keep prerequisites and safety checks visible.
3. Check relative links, heading anchors, code fences, and closed hint blocks. Run `git diff --check` locally. Do not add or use GitHub Actions.
4. Explain what changed, why it helps, and how you checked it. Mark untested device or runtime claims plainly.
5. Open a pull request when the public repository is available. Keep upstream credits intact.

## Share evidence safely

For a correction, include the guide section, expected result, actual result, and relevant hardware/software versions. Prefer a small, redacted text excerpt over a full log. Remove usernames, local paths, addresses, identifiers, and secrets before sharing.

Never attach game files, decrypted executables, keys, keystones, saves, or full disc images. Do not include third-party binaries in a patch. Existing components retain their own licenses.

For runtime results, distinguish unit checks, startup, rendering, input, saves, and sustained play. Include the revision and test conditions. Do not call a title screen a complete gameplay test.

## Document headers

Keep the standard document header. Update its date and version when needed. Use `docseal anchor` before committing changed header-bearing files; if anchoring is unavailable, use `docseal stamp` and record the reason. An unanchored document must not claim a transaction. Never ask contributors to share signing keys.

## License gate

The project owner has not selected an open-source license for this preparation branch. Resolve that before requesting outside code contributions or presenting the project as open source.
