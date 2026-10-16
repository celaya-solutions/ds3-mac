```text
Document:    The Pilgrimage — A Dark Souls III Mac Learning Quest
Version:     v1.2.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      134ea65769ef12bdcfe6ed3103f078ab60687e29e1aa422e07022c5047b29afb
Chain:       solana-mainnet
Tx:          mYegVWnbjCP6qVsZFuT1fHbjj9oMkrAjx9YuqTFjnuFXLaJMdb7UwLJtHpHj5EwtoWpuMurWbC5npoDB32ftRhS
License:     All Rights Reserved / Celaya Solutions
```

# The Pilgrimage

[Choose another path](../README.md#choose-your-path) · [Companion prompt](companion.md)

*No summon can take the controller from your hands. A good one can teach you where to look.*

This quest teaches the same backup workflow as the [regular tutorial](regular.md). Try each question, open a hint if you need one, then read the answer. You do not have to earn access to a safety instruction.

**Always visible:** use your own disc and files. Keep the PS4 offline and its firmware unchanged. Never format storage. Choose an approved destination. Confirm exact firmware support before any loader step. The recorded setup used 11.02; other versions are not covered by that result. This path ends at a checked backup, not proven Mac playability.

## I · Name the traveler

**Before you act:** record your Mac and macOS version, exact PS4 firmware, disc edition, installed updates, and any previously working loader. Identify drives that must stay untouched.

**Question:** why is “my console runs version 11” not enough information?

<details>
<summary>Hint · read the final digits</summary>

A version number describes a particular system. A tool’s support list needs to describe that same system.

</details>

<details>
<summary>Answer · names bind the route</summary>

11.00 and 11.02 are different firmware versions. A loader that supports one is not evidence of support for the other. Check the complete version in Settings → System → System Information, then check exact support and the saved loader files. If support is unknown, stop that step.

Follow [regular tutorial step 1](regular.md#1-check-your-setup-first).

</details>

**Bonfire:** you can name the exact setup and explain why its loader is suitable. If you cannot, the next task is research, not an attempt.

## II · Lay a bridge with no road beyond it

**Before you act:** connect the PS4 to the Mac by Ethernet. Keep it disconnected from router and Wi-Fi. Internet Sharing must stay off. Save current network settings before a needed change.

**Question:** can two devices exchange files without reaching the internet?

<details>
<summary>Hint · the cable has two ends</summary>

Local communication and internet routing are different things.

</details>

<details>
<summary>Answer · a small, closed world</summary>

Yes. The Mac and PS4 can communicate over a local Ethernet link without an internet route. Check the cable, adapter, addresses, and subnet. The addresses in the regular tutorial are examples, not settings to copy blindly. A USB cable between the devices does not turn the Mac into a storage drive.

Follow [regular tutorial step 2](regular.md#2-keep-the-ps4-off-the-internet).

</details>

**Bonfire:** the local link works, and you have checked that the PS4 has no internet path.

## III · A lit doorway is not an open gate

**Before you act:** use the saved, verified loader for your exact firmware. Do not accept a system update. Do not repeat failed attempts indefinitely.

**Question:** the loader page opens. What has that proved, and what has it not proved?

<details>
<summary>Hint · separate the page from the console</summary>

One observation concerns a web server. The next concerns what the console is running.

</details>

<details>
<summary>Answer · ask the gate itself</summary>

The page opening shows that the browser can reach the loader page. It does not prove GoldHEN loaded. Check for the GoldHEN menu, then enable its FTP server and check the reply. A server banner is evidence of a reachable service, not a completed backup.

Follow regular tutorial [step 3](regular.md#3-start-the-saved-loader-on-the-mac), [step 4](regular.md#4-load-goldhen-on-the-ps4), and [step 5](regular.md#5-check-the-file-connection). For a failure, record the error and use the guide’s bounded recovery notes.

</details>

**Bonfire:** you can show the console state and the file service reply, rather than only a browser title.

## IV · Carry only what is yours

**Before you act:** choose a new folder on an approved drive and check free space. Keep the disc inserted and the game open. Keep the Mac awake and the cable connected. Never overwrite an older backup.

**Question:** why record the game’s title ID and version before copying it?

<details>
<summary>Hint · two discs can share a name</summary>

A game title alone does not identify its release, region, or update state.

</details>

<details>
<summary>Answer · label the burden</summary>

The title ID and version identify the source being tested. Record mounted updates and extra content too. The documented run used CUSA03388 version 1.00, with no mounted update or extra content. Your files may differ. Saves are a separate backup task; do not assume they were copied with the game.

Follow [regular tutorial step 6](regular.md#6-open-the-game-and-copy-it). Keep source lists, logs, game files, and the keystone private.

</details>

**Bonfire:** the copy finishes without error, and you know exactly which release it contains. Do not close the game until verification finishes.

## V · Distrust the full bar

**Question:** every file appears present, but a decrypted program file is smaller than its source. Is that necessarily a failed copy?

<details>
<summary>Hint · ask what transformation occurred</summary>

A byte-for-byte copy and a decrypted output do not have the same size rules.

</details>

<details>
<summary>Answer · inspect the evidence</summary>

No. Decrypted program files can be smaller. Check their format rather than treating every size change as a missing transfer. Compare the full source list, check ordinary file sizes, record checksums, and compare a few files with fresh reads. A checksum you just made is a useful future baseline; by itself it does not prove that the source was copied correctly.

Follow [regular tutorial step 7](regular.md#7-check-the-backup-before-you-stop). Only after those checks pass should you close the game.

</details>

**Bonfire:** write three lines: what passed, what differs, and what remains untested.

## VI · The next fog gate

**Question:** what would a complete backup tell you about whether DS3 can run on a Mac?

<details>
<summary>Hint · a map is not a journey</summary>

Think about which program has actually executed during this lesson.

</details>

<details>
<summary>Answer · leave the claim where the evidence ends</summary>

It shows that you have checked local input files. It does not show that a Mac runtime can load the program, resolve its imports, render a scene, or support a playable session. Each needs its own observation. The recorded runtime test is a separate observation; see [its conditions and limits](runtime.md). Your backup alone cannot reproduce that claim.

</details>

**Your first contribution:** explain one gate in your own words, or report a confusing step with the expected and observed result. Read [contributing](../CONTRIBUTING.md) before sharing logs.

*Rest here. Keep your notes. The next traveler should find a clearer road.*

## VII · Read the runes

**Before you act:** you can run `python3 -m unittest -v` without a console or game files. Runtime tests require the inputs listed in the [runtime guide](runtime.md). Do not download someone else’s game files to complete this lesson.

**Question:** two game executables use the same short library ID. Why might binding their imports by that ID alone call the wrong function?

<details>
<summary>Hint · names have a home</summary>

Ask whether the short ID belongs to the whole platform or to one executable’s own table. Look at the collision test in `test_import_adapter.py` when you are ready to inspect an example.

</details>

<details>
<summary>Answer · translate the identity, not the letter</summary>

The IDs are local to each executable. The adapter reads the library and module identities, including their versions, then maps them to the reference executable’s IDs. An unrelated library must not inherit a matching short ID. Read `canonical_name` in `import_adapter.py`, then the collision and version-mismatch tests. Predict their results before running them.

</details>

**Bonfire:** explain why names *and versions* matter. Then run the six tests and read the test that checks that bytes outside import-name slots stay unchanged. For a live experiment, continue to the [runtime guide](runtime.md) and record your own observations.
