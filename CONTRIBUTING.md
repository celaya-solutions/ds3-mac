```text
Document:    Contributing to Dark Souls III on Mac
Version:     v1.3.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      6827ca86967f49ce1053fad0d7bd2b128db44ec1fa7737ff4c59b7071ebf8f27
Chain:       solana-mainnet
Tx:          sV7f9j5QvS16o19MnpRobT8EwWEt5y1Kz28Q6KsQX6S9ne6VDQKc6tN43C1WB2bNb1utqv2jjKBmVQb7AfBVFvL
License:     MIT / CSR (Celaya Solutions)
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

All original code and documentation use the [MIT License](LICENSE.md). Contributions use the same terms. Keep the copyright and license notice crediting CSR (Celaya Solutions). Only submit work you have the right to share.
