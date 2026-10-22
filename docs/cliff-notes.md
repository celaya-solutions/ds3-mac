```text
Document:    The Homeward Bone — Dark Souls III Mac Cliff Notes
Version:     v1.3.2
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-21
SHA256:      b26c51f0ed4b34c431eab94407d0c84e2a4b9b2d23ce81c10143479e6d23f332
Chain:       solana-mainnet
Tx:          3q4ghz85cwyVoVU9C7E4UTYmiFLYwttUGqbExA5j8rZQfqrqnfTMQnx2tRErk2jS2dHVQsnNBFNnaTj2LcqHKgR8
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

Run `python3 -m unittest -v` for the adapter, launcher, and restart tests; no game files are needed. To try the game, read [runtime requirements](runtime.md) and use explicit paths to your own DS3 files, supported Bloodborne reference, and bbport installation. Record startup, rendering, input, and save behavior separately. Do not treat an exit code or frame counter as proof of a complete gameplay test.
