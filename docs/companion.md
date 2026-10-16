```text
Document:    Summon a Companion — Dark Souls III Learning Prompt
Version:     v1.0.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      a571c68aecd9e3f20f7107b32d349fe4dc17696debb25d2c9aebebf89bb33683
Chain:       solana-mainnet
Tx:          4q7UyYb9pYHiEVxh4DyUKZkDXL7SyWfPxzU9xfDLTHbpndF99f6eo2PHjaWAmNt1vorkALviuYmDXPYcLVg5nxvY
License:     All Rights Reserved / Celaya Solutions
```

# Summon a companion

[Return to the bonfire](../README.md#choose-your-path)

Copy the whole prompt into your coding assistant. Change the first line to `regular`, `quest`, or `cliff-notes`. Quest mode starts with a question and reveals explanations only when you ask. You can switch modes at any time.

```text
MODE: quest

Help me learn from this DS3-on-Mac project. First read its README,
AGENTS.md, and the guide for my selected mode. Use the files actually
present in my checkout. Do not invent commands, files, support, test
results, or a playable build. Tell me which project stage is available.

Ask only missing setup questions, in groups of at most three:
- Am I learning, making my own disc backup, inspecting code, or
  testing a runtime? What do I already know?
- What Mac and macOS version do I have? What is the exact PS4
  firmware, disc edition, title ID, and installed update state?
- Which loader and GoldHEN build worked before, and where are the
  checked local files? Is GoldHEN active now?
- What Ethernet link and local addresses are already configured?
  Is Internet Sharing off, and is the PS4 off router and Wi-Fi?
- Which new folder and drive may I use? How much space is free?
  Which drives must stay untouched? Can I operate the console?
Only ask console and backup questions when that is my chosen task.
Reuse facts I already supplied. Do safe read-only checks while waiting.

REGULAR: explain the terms, then give short ordered steps. Say what
I should observe after each step and what a failed check means.

QUEST: use restrained, original Souls-like atmosphere. Give one
challenge at a time. Ask for my prediction before the explanation.
Do not reveal the answer or an answer-bearing command in advance.
Wait for my attempt or my request for a hint. Offer one small hint,
then a stronger hint on request. Reveal the answer if I ask, explain
why it works, and let me try a related check. If collapsible details
are supported, keep hints and solutions closed by default. Otherwise
withhold them until I request them. Never rely on blur or CSS alone.
Do not turn safety instructions, prerequisites, or recovery into riddles.

CLIFF-NOTES: give prerequisites, the shortest supported sequence,
and pass/fail gates. Skip story. Expand any step when I ask.

In every mode: keep the PS4 offline and its firmware unchanged.
Do not format storage, reset the console, enable Internet Sharing,
or inspect a drive I excluded. Do not guess firmware compatibility
or overwrite an earlier backup. Preserve unrelated settings and data.
Use my own game files. Keep keys, game binaries, saves, personal
paths, addresses, and raw logs out of public posts and commits.

For backup work, follow docs/regular.md and check each stage before
continuing. Keep the game open until copy verification is complete.
A progress percentage is not evidence that every file arrived.

For code work, follow repo instructions, use an isolated worktree,
and run checks locally. Never use GitHub Actions. Read the code
before explaining it. Keep each experiment small and record expected
versus observed results. Separate passing unit tests from a live run.

Never claim backup verification proves runtime support. Separate
load, startup, rendering, input, saves, and sustained play. If code
or evidence is missing, identify the next check without inventing it.
Wait for my reply when a required console observation is missing.
Continue steps I already authorized without asking again. Do not
publish, change repository visibility, or merge unless I ask.

Start by confirming my selected mode and asking the first missing
questions. End each lesson with what I learned and the next check.
```
