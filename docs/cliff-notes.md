```text
Document:    The Homeward Bone — Dark Souls III Mac Cliff Notes
Version:     v1.3.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      66a0885bcc096b2461dbee98128a26a0ea11fa8de6de260e9786424e29b52da1
Chain:       solana-mainnet
Tx:          45Jngv9Schrd6K5obxeqwdSBFji71RMpMrEaEKxfrYkdUbTUmuAdKr6RSYjMBfELkUTWrczM7MxDQ5GJu7dq5Mev
License:     MIT / CSR (Celaya Solutions)
```

# The Homeward Bone

[Choose another path](../README.md#choose-your-path) · [Companion prompt](companion.md)

**Scope:** backup first, then an optional runtime experiment. A backup alone does not prove playability. The [runtime guide](runtime.md) lists the exact inputs and the limits of the recorded early gameplay test.

## Before you start

Own the disc. Know the exact PS4 firmware, supported loader, game release, Mac setup, approved destination, and free space. Keep the PS4 offline and its firmware unchanged. Never format a drive. Keep game files, keys, saves, and raw logs private.

The recorded run used PS4 11.02 and CUSA03388 v1.00. Do not treat that as support for a different setup.

## The route

1. **Identify:** record exact firmware and game version; verify loader support. Unknown support means stop and check.
2. **Connect:** local Ethernet; Internet Sharing off; no PS4 router or Wi-Fi connection. Save old network settings before changes.
3. **Load:** serve the verified local loader. Check the GoldHEN menu, then its FTP reply. A loaded web page is not enough.
4. **Copy:** launch the installed disc game; record mounted content. Check backup-tool requirements and free space. Copy to a new approved folder. Keep the game open and Mac awake.
5. **Verify:** successful tool exit, complete source list, ordinary file sizes, decrypted code format, saved checksums, and fresh-read samples. Do not trust the percentage alone.
6. **Record:** write what passed and what remains untested. Then close the game. Mac execution is a separate test.

Need commands or recovery details? Use the [regular tutorial](regular.md). These cliff notes are a checklist, not a replacement for exact-version instructions.

## The prompt

Copy the [companion prompt](companion.md) and set `MODE: cliff-notes`. It asks only missing setup questions, gives a compact route, and keeps device checks visible.

## Code route

Run `python3 -m unittest -v` for the six adapter tests; no game files are needed. To try the game, read [runtime requirements](runtime.md) and use explicit paths to your own DS3 files, supported Bloodborne reference, and bbport installation. Record startup, rendering, input, and save behavior separately. Do not treat an exit code or frame counter as proof of a complete gameplay test.
