```text
Document:    Back Up a PS4 Game Disc to a Mac While Staying Offline
Version:     v1.3.0
Author:      Celaya Solutions
Contact:     hello@celayasolutions.com
Date:        2026-10-16
SHA256:      f2c486e80c1d14129d95d1b28b38e6ea7fa62aea63479715361fd692267fa310
Chain:       solana-mainnet
Tx:          3mT3Ve2mmVkD24ZCuTiPDtJyRzDruP9FYGUbWnhT5MrPR3LCVqQNC98z9DY3XZ96Jo3NPpauwA64nho8xbnNe65y
License:     MIT / CSR (Celaya Solutions)
```

# Back up your PS4 game disc to a Mac

[Choose another path](../README.md#choose-your-path) · [Companion prompt](companion.md)

This is the regular path: the full steps and explanations are visible. For questions with optional hints, take the [quest](quest.md). For a compact checklist, use the [cliff notes](cliff-notes.md).

This guide shows how I copied my Dark Souls III disc to my Mac. The PS4 stayed off the internet, and its system software did not change.

The result is a folder of game files. It is not an installer. This guide does not test whether the game runs on a Mac.

## What you need

- Your PS4 and your own game disc.
- A TV or screen and a PS4 controller.
- A Mac with enough free space for the full game.
- An Ethernet cable.
- A USB-C Ethernet adapter if your Mac has no Ethernet port.
- A loader that works with your exact PS4 system version.
- A backup tool such as [ftpdump](https://github.com/hippie68/ftpdump).

**You do not need a USB storage drive for this network copy.** A USB cable between the PS4 and Mac does not turn the Mac into a storage drive.

Our backup used about **17.8 GB**. Your copy may need more space if it has updates or extra game content.

## A few words to know

- **Firmware:** the PS4's system software. A game update is a different thing.
- **Loader:** the page or tool that starts the jailbreak.
- **GoldHEN:** software that lets the PS4 run homebrew tools. Homebrew means apps made outside Sony's normal store.
- **FTP:** a way to copy files over a local network.
- **Checksum:** a code made from a file. It helps you check whether that file changed.

## 1. Check your setup first

On the PS4, open **Settings → System → System Information**. Write down the full version number. Do not share the console's serial number.

My PS4 used **11.02**. The saved setup used the **CSSFontFace/Lapse** browser loader, **GoldHEN v2.4b18.7**, and a patch made for **11.02**.

Those parts worked together in this run. A guide for 11.00 is not proof that the same files work on 11.02. Check the exact loader and files before you use them.

Tell your agent which drives it may use. I used the Mac's internal storage. My external SSD was off-limits.

## 2. Keep the PS4 off the internet

Connect the PS4's Ethernet port to the Mac's Ethernet adapter.

On the Mac, open **System Settings → General → Sharing**. Make sure **Internet Sharing is off**. Do not bridge this cable to a network that has internet access.

Keep the PS4 disconnected from your router and Wi-Fi. Do not accept a system update. A local Ethernet link can work without internet access.

Ask the agent to check the cable link and the saved network settings. It should save the old settings before it changes anything.

These were our local addresses:

| Device | Address |
| --- | --- |
| Mac Ethernet port | `192.168.50.1` |
| PS4 | `192.168.50.2` |
| Subnet mask | `255.255.255.0` |

These are examples from our setup. Reuse them only if they fit your network. The Mac's Ethernet settings had no router address.

## 3. Start the saved loader on the Mac

Have the agent find the loader you used before. It should check the files and start the local web server.

Our page was:

**https://192.168.50.1:8443/public/**

That page came from the Mac, not an internet website. It only works while the Mac's loader is running and the cable link is active.

If the page does not open, check the cable and adapter first. In our run, the adapter showed no link until it was reconnected. The agent then started the loader and checked that its files were served correctly.

## 4. Load GoldHEN on the PS4

Open the local page in the PS4 browser. For our saved 11.02 setup, **Lapse** was the chosen option.

Let **Auto Jailbreak** run once if it is checked. Do not press the Jailbreak button over and over while it runs.

The page title “CSSFontFace UAF Exploit” does not mean GoldHEN has loaded. Wait for the result, then check for the **GoldHEN** menu in the PS4's settings.

### If the attempt fails

Our first attempt showed race errors, then “Environment cleanup started,” then “Invalid value of type undefined at arg 0.” GoldHEN did not load.

We saved and closed the game, chose a normal **Restart PS4**, and tried the same saved Lapse loader again. The next attempt worked. A normal restart does not mean choosing an update.

If it fails again, send the agent a photo of the error and the lines just above it. Do not switch loader types at random.

GoldHEN normally needs to be loaded again after a full restart or shutdown. Its menu going away is expected. Installed app icons going away is a separate issue to check if it continues.

## 5. Check the file connection

In **GoldHEN → Server Settings**, turn on the **FTP Server** if needed. Menu names may differ by build.

Our PS4 used port **2121**. The agent confirmed this reply from the console:

```text
220 GoldHEN FTP server v2.2
```

That reply confirms the FTP service is active. If the connection is refused, check that GoldHEN loaded and FTP is turned on. The `v2.2` in this reply names the FTP server, not the full GoldHEN release.

## 6. Open the game and copy it

Insert your disc. Make sure the game has finished installing from the disc. Launch it and leave it at the title screen.

The agent should now check the mounted game. Our game was **DARK SOULS III**, title ID **CUSA03388**, version **1.00**. A title ID is the code for that game release.

Have the agent create a new backup folder on the approved drive. It should use the tested backup tool to copy the game, any mounted update or extra content, and the game's keystone file. Keep that small key file with your private backup.

If the agent uses `ftpdump` on a Mac, it needs **GNU Wget** and a supported Bash version. It should check those tools first; the Mac's older built-in Bash may not work.

During the copy:

- Keep the game open and the disc inserted.
- Keep the Mac awake.
- Leave the Ethernet cable connected.
- Do not restart either device.

The agent should track the bytes copied and watch for errors. In our run, one size reply was too small, so the tool's percent reached 100% early. The full file list gave the right total. **A progress bar alone is not proof that the copy is done.**

## 7. Check the backup before you stop

Ask the agent to check that:

- The copy tool finished without an error.
- Every game file in the source list is present.
- Ordinary file sizes match the source list.
- The game program and its needed code files were decrypted correctly.
- Checksums were saved for all backup files.
- A few files match fresh copies read from the PS4.

Decrypted program files can be smaller than their original files. The agent should check their format instead of treating every size change as a failed copy.

Our finished backup contained all **12,299 source files**, plus extra game details added by the backup tool. It totaled **12,319 files** and about **17.8 GB**. Four decrypted code files passed checks, and three files matched fresh reads from the PS4.

No game update or extra content was mounted in this run. The backup is version **1.00**. Saves were not included. Running the game on a Mac is a separate task that still needs a real play test.

Once these checks pass, you can close the game. Keep the backup private and keep its checksum files with it.

## Copy this prompt for your agent

```text
Help me back up my own PS4 game disc to my Mac's internal storage.
Keep the PS4 off the internet and keep its firmware unchanged.
Write short, clear steps at a sixth-grade reading level.

Start by reading any setup notes I give you. Reuse facts that are
already clear. Ask the missing questions in small groups:

1. What is the exact version under PS4 Settings → System →
   System Information? Which disc game and edition do I own?
2. Has the disc finished installing? Does the game launch?
   Are any game updates or extra content already installed?
3. Is GoldHEN active now? Which loader, GoldHEN build, and
   firmware patch worked before? Where are the saved files?
4. What Mac and macOS version am I using? Is the PS4 connected
   by Ethernet? Which adapter is in use? Is “USB” a storage
   drive, an Ethernet adapter, or a cable between the devices?
5. Which folder and drive may hold the backup? How much space
   is free? Which drives and files must you leave alone?
6. Is Internet Sharing off? Is the PS4 disconnected from the
   router and Wi-Fi? What local addresses are already set?
7. Can I use the PS4 controller and report what the TV shows?
   Do I want only the game backup, or a separate save backup too?

Do safe read-only checks while waiting for my answers. Do not
guess a drive, firmware version, or loader. Do not inspect any
drive I say is off-limits. Do not show passwords, keys, or tokens.

Once the needed facts are clear, do the work. Do not keep asking
for permission for steps I have already approved. Ask me to do
console steps you cannot do, and wait for my reply when needed.

Never update, reset, or initialize the PS4. Never format a drive.
Do not enable internet sharing, change unrelated network settings,
or download PS4 system updates. Save the old network settings
before any needed change. Never assume an 11.00 loader works
on 11.02. Check exact-version support and saved file hashes.

Use the previously working offline loader when it is available.
Check the Ethernet link and start the loader on the local address.
Confirm the page works. Guide me through loading GoldHEN.
A page title or a running web server is not proof of success.
Check the GoldHEN menu and the FTP server reply.

If Lapse fails and then reports a cleanup error, record the error.
For the known 11.02 setup, a normal restart and one fresh attempt
worked before. Do not promise it will fix every failure. Do not
repeat attempts forever or switch methods without checking support.

Ask me to launch the installed disc game and leave it at its title
screen. Read the mounted game's title ID and version. Check free
space, then make a new backup folder on the approved drive.

Use a trusted, checked backup tool such as ftpdump. Check its Mac
tools and requirements first. Copy the base game, mounted updates
and extra content, and its keystone. Do not mix files from another
game or overwrite an older backup. Treat saves as a separate task.

For ftpdump, use --app --patch --dlc --keystone and --output-dir
with the approved new folder and the checked PS4 address and port.
Use the correct Bash version and an explicit path to the tool.

Keep a transfer log and a source file list. Track real bytes copied;
some FTP size replies or progress bars may be wrong. If the copy
stops, check whether this tool and server can safely resume it.

Before calling the backup complete, check the tool's exit result,
missing files, file sizes, and decrypted program files. Save a
SHA-256 checksum list. Compare a few files against fresh PS4 reads.
Explain exactly what passed and record any limits in the backup
notes. Do not claim Mac playability without a real play test.

Finish with a short result, a link to the backup folder, the game
version, and whether it is safe for me to close the game.
```

## Tool sources

- [CSSFontFace/Lapse loader](https://github.com/ntfargo/CSSFontFace-Exploit)
- [GoldHEN](https://github.com/GoldHEN/GoldHEN)
- [ftpdump and its instructions](https://github.com/hippie68/ftpdump)

These projects can change. Check their current instructions and your saved setup before using a new release.

## Next: understand and test the adapter

Your backup is an input, not a guarantee that a runtime supports it. Continue with the [runtime guide](runtime.md) for the exact requirements, launch command, code explanation, and recorded test limits. The [quest’s code lesson](quest.md#vii--read-the-runes) asks you to predict the import problem before revealing the explanation.
