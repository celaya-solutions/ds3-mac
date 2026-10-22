```text
Document:    Dark Souls III on Mac — The Next Bonfire
Version:     v1.4.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-21
SHA256:      61fdffa28ee69f935ba655857bb34860d6dc3a4e026e3070156f68bd61e608f2
Chain:       solana-mainnet
Tx:          JGy7Mqjqt28m2MEwtcnYKbn6UWH2has64RRoNcKFnEJ2ZJyE1KHEcSBdEPHjNrkkGqTLBWFRPGQYwor7TRp3Wn3
License:     MIT / CSR (Celaya Solutions)
```

# DARK SOULS III · MAC

*The hunt ended. An ember remained.*

A follow-up to Celaya Solutions’ Bloodborne-on-Mac work. This time, the road leads to Lothric.

Before you touch the code, learn what you are carrying: your own game, a backup you can trust, and evidence that tells you what actually worked. Pick a path. You can change it at any bonfire.

> **Current state:** an early compatibility experiment, with an import adapter, launcher, eleven local tests, and three learning paths. The recorded October 16 test reached Cemetery of Ash: walking and a sword swing worked, with the overlay near 30 FPS. This is not a full-game or sustained-performance result. See [requirements and test limits](docs/runtime.md).

## Choose your path

| Path | What you get | Begin |
| --- | --- | --- |
| **The Road — regular tutorial** | Plain steps, terms explained, checks along the way. | [Start the tutorial](docs/regular.md) |
| **The Pilgrimage — quest mode** | Questions first. Optional hints. Answers sealed until you open them. | [Enter the quest](docs/quest.md) |
| **The Homeward Bone — TL;DR / cliff notes** | Requirements, gates, and the shortest honest route through them. | [Read the cliff notes](docs/cliff-notes.md) |

**Bringing an AI companion?** [Copy the prompt](docs/companion.md), choose your path, and have it ask about your setup before it gives instructions.

## Read this before crossing the fog

- Supply your own game disc, console, and local files. No game assets, executables, keys, or saves belong in this repo.
- The backup walkthrough describes a PS4 **11.02** setup. A different firmware version needs its own verified support. Do not guess.
- Keep the PS4 offline and its firmware unchanged. Never format a drive or change an unrelated device to follow a lesson.
- A complete backup is one milestone. A successful launch, a rendered frame, and a playable session are separate milestones.

These facts stay visible in every path. Hints and explanations can be hidden; requirements cannot.

## Your first bonfire

Before opening a solution, answer this:

**A copy progress bar says 100%. What would convince you the backup is actually complete?**

<details>
<summary>Spend an ember · a small hint</summary>

A progress bar reports what a tool believes. Look for evidence you can check independently.

</details>

<details>
<summary>Read the inscription · the answer</summary>

Check that the tool finished successfully. Compare the source file list with the copy, check ordinary file sizes, verify decrypted code files by format, and save checksums. Compare a few files with fresh reads from the console. Explain any mismatch before continuing.

The [quest](docs/quest.md) teaches why each check matters.

</details>

## Beyond the bonfire

Continue with the [runtime guide](docs/runtime.md) after your backup is checked. You need a compatible, separately installed **bbport 0.4-v1 runtime**, your own **DS3 CUSA03388 v1.00** files, and your own supported **Bloodborne reference executable**. This repo does not install or bundle those inputs. You can also [use a built bbport checkout](docs/runtime.md#use-the-local-bloodborne-runtime-improvements) with the local Bloodborne renderer improvements and play until you quit with `--timeout 0`.

To work on the adapter without game files:

```sh
git clone https://github.com/celaya-solutions/ds3-mac.git
cd ds3-mac
python3 -m unittest -v
```

Use the **Fork** button first if you want to contribute from your own GitHub copy. The [quest](docs/quest.md#vii--read-the-runes) gives you a question before explaining the adapter.

Want to help? Start with [contributing](CONTRIBUTING.md). A small, well-supported correction is a useful first contribution.

## Credits and boundaries

DARK SOULS III and Bloodborne belong to their respective rights holders. This is an independent fan research project, unaffiliated with FromSoftware, Bandai Namco, or Sony. The quest language is original; no game art or dialogue is bundled.

The backup workflow builds on [CSSFontFace/Lapse](https://github.com/ntfargo/CSSFontFace-Exploit), [GoldHEN](https://github.com/GoldHEN/GoldHEN), and [ftpdump](https://github.com/hippie68/ftpdump). Those projects retain their own licenses and credits.

**License:** all original code, tests, guides, and prompts are open source under the [MIT License](LICENSE.md). Use, change, share, or sell them; keep the copyright and license notice crediting **CSR (Celaya Solutions)**. Third-party games, runtimes, and tools retain their own licenses.
