```text
Document:    Contributing to Dark Souls III on Mac
Version:     v1.2.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      0c1cf11568cc250bf4d412ce8d680aacbb6f642e784225d914fcf022e6d390c8
Chain:       solana-mainnet
Tx:          5Xw9bSXHsaygNr9ywgG3xYUgRnzDxYFmk2HF25fY2RYRNGms7jc7wj2vJ37LidoetrAyJSoSLiH48PYin8uZNLLA
License:     All Rights Reserved / Celaya Solutions
```

# Leave a clearer road

Start with the [README](README.md) and choose a learning path. The project contains a small import adapter, a launcher, local tests, and learning guides. Read the [runtime guide](docs/runtime.md) before making compatibility claims.

Useful first contributions include a clearer explanation, a broken-link fix, a better hint, or a reproducible correction to a setup step.

## Send a focused change

1. Fork [celaya-solutions/ds3-mac](https://github.com/celaya-solutions/ds3-mac) on GitHub. Clone your fork and create a branch or isolated worktree for your change.
2. Keep the change small. Preserve all three learning paths. Hide optional explanations behind closed `<details>` blocks in quest mode; keep prerequisites and safety checks visible.
3. Check relative links, heading anchors, code fences, and closed hint blocks. Run `python3 -m unittest -v` and `git diff --check` locally. Do not add or use GitHub Actions.
4. Explain what changed, why it helps, and how you checked it. Mark untested device or runtime claims plainly.
5. Open a pull request. Keep upstream credits intact.

## Share evidence safely

For a correction, include the guide section, expected result, actual result, and relevant hardware/software versions. Prefer a small, redacted text excerpt over a full log. Remove usernames, local paths, addresses, identifiers, and secrets before sharing.

Never attach game files, decrypted executables, keys, keystones, saves, or full disc images. Do not include third-party binaries in a patch. Existing components retain their own licenses.

For runtime results, distinguish unit checks, startup, rendering, input, saves, and sustained play. Include the revision and test conditions. Do not call a title screen a complete gameplay test.

## Document headers

Keep the standard document header. Update its date and version when needed. Use `docseal anchor` before committing changed header-bearing files; if anchoring is unavailable, use `docseal stamp` and record the reason. An unanchored document must not claim a transaction. Never ask contributors to share signing keys.

## License

Original Python code uses MIT; project documentation uses CC BY 4.0. Contributions use the same terms as the material they change. See [license terms](LICENSE.md). Only submit work you have the right to share.
