# 🌌 h4 Mantella Omni-Tool (v1.0b) | SENTIENT MIDDLEWARE

> *"Because giving NPCs a soul shouldn't require a degree. But we used one to build this anyway."*

---

# So, what is this thing?

Okay listen. You want to talk to Skyrim NPCs. You want them to talk back. You saw a video on YouTube and thought "that looks cool" but then you saw the installation instructions involved Python, CLI terminals, localhost ports, and editing INI files. You almost clicked away.

**Don't panic. That is why I built this.**

This tool is your easy button. It is **"Sentient Middleware."**
Normally, getting AI to talk to Skyrim is like trying to teach a cat calculus. The game is old. The AI is new. They hate each other.
This tool forces them to get along. It assumes your PC is broken, your ports are blocked, and your paths are wrong—and it fixes them without asking.

### What it does for you:
1.  **Finds your game**: You don't need to tell it where Skyrim is. It uses the **Hunter Protocol** to scan every drive on your system.
2.  **Installs the boring stuff**: It handles all the Python libraries (CustomTkinter, Requests, PyWin32) locally. You don't need Python installed.
3.  **Fixes the bugs**: There are about fifty tiny bugs in the original mod setup (Port 5000 vs 4999, Icon Caching, Firewall Rules). We squashed them all.
4.  **The Neural Bridge**: It sits between the game and the AI, listening to your conversation. If the AI forgets to open a trade menu, the Bridge forces it open.

---

# ⚠️ Hardware Reality Check (Read This First!)

> *"My GPU is screaming, is that normal?"*
> *Yes. It's thinking.*

AI isn't magic. It's math. Heavy, hot, expensive math. Before you blame the tool for lagging, check your rig.

## A. The "Cold Start" (Patience is a Virtue)
When you first launch the game (or the tool), **Ollama needs to load the model into VRAM.**
*   **Time:** 30 seconds to **5 MINUTES**.
*   **Symptom:** You say "Hello", and the game freezes or does nothing.
*   **Reality:** The lower your system specs, the longer this takes. **DO NOT PANIC.** Just wait.

## B. The VRAM Guide (Video Memory)
If the model doesn't fit in VRAM, it runs on your CPU, which is 50x slower.
*   **8GB VRAM**: Use `llama3:8b` (Quantized). Don't run 4K Graphics Mods + AI.
*   **12GB VRAM**: The Sweet Spot. Use `hermes-2-pro-llama-3`.
*   **24GB VRAM**: God Mode. Use `command-r` or `mixtral`.

---
---

# Dev Read Me (The Technical Grimoire)

> *Everything below this line is for the nerds, or if you actually care how the sausage is made.*

# 📚 The Index
1.  [**Prologue: The Philosophy**](#1-prologue-the-philosophy)
2.  [**System Architecture**](#2-system-architecture)
3.  [**Feature Deep Dive**](#3-feature-deep-dive)
4.  [**User Manual: Operations**](#4-user-manual-operations)
5.  [**Troubleshooting**](#5-troubleshooting)

---

# 1. Prologue: The Philosophy

The *Mantella* mod is a technical marvel, but its installation profile is "hostile." It relies on users manually editing `Skyrim.ini` to enable Logging, forwarding ports in Windows Firewall, and matching DLL versions.

The **h4 Omni-Tool (v1.0b)** is designed as a **Single-File Solution**.
*   **No Dependencies**: It compiles into a standalone EXE using `PyInstaller`.
*   **Self-Healing**: It checks `Skyrim.ini` on every launch. If logging is disabled, it surgically re-enables it without destroying your other settings.
*   **Atomic Operations**: When writing config files, it uses atomic swaps to prevent corruption during crashes.

---

# 2. System Architecture: The "Three Nations"

## A. The Hunter (Heuristic Scanner)
*Source: `core/scanner.py`*
Most installers are dumb. They look in `C:\Program Files` and give up. The Hunter is relentless.
*   It checks Registry Keys for Steam.
*   It scans `C:\Games`, `D:\Games`, `Z:\Games`.
*   It identifies Mod Organizer 2 instances by looking for `ModOrganizer.exe` and pivots to the `mods/` folder.

## B. The Bridge (Neural Interceptor)
*Source: `core/bridge_server.py`*
This is the core innovation. The Omni-Tool acts as a **Man-in-the-Middle** proxy between Skyrim (Port 5001) and Ollama (Port 11434).
*   **Problem**: Users ask "Show me your wares." The AI says "Sure!" but forgets to output the `[inventory]` tag required by the mod.
*   **Solution**: The Bridge sniffs the traffic. It detects keywords like "buy", "sell", "trade". If found, it **Force Injects** the `[inventory]` tag into the AI's response stream. The game sees the tag, and the menu opens. Magic.

## C. The Surgeon (INI Management)
*Source: `utils/ini_surgeon.py`*
Editing `.ini` files by hand is dangerous. The Surgeon uses a custom parser to locate `[Papyrus]` sections and ensure `bEnableLogging=1`, `bEnableTrace=1`, and `bLoadDebugInformation=1` are active. It backs up your original file (`Skyrim.ini.bak`) before touching anything.

---

# 3. User Manual: Operations

### First Time Setup (The Ritual)
1.  **Launch**: Run `h4 - Mantella Omni Tool (v1.0b).exe`.
2.  **Wizard**: The First-Run Wizard will appear. Let it scan.
3.  **Configure**: Click **[2] CONFIGURE**. Select your AI Model.
4.  **Activate**: Click **[3] ACTIVATE SERVICES**.
    *   *Wait for "Ollama Server Running".*
5.  **DONG**: Launch Skyrim. Wait at the Main Menu until you hear a "DONG" sound. That is the handshake.

### The Codex Gigas
We included the manual *inside* the app. Click **Help -> Codex** to open the "Codex Gigas," a built-in encyclopedia explaining every error code, feature, and setting in hyper-detail.

---

# 4. Troubleshooting

### "Waiting for Player Input..."
**Cause:** The game cannot talk to the tool (Port Mismatch).
**Solution:** Go to **[2] CONFIGURE** and click **Save Configuration**. This regenerates the config with the new "Dual Port" fix (4999 in both sections).

### "Ran out of Memory" Popup
**Cause:** You are running the Tool + Chrome + Skyrim + Ollama (8GB Model) on 16GB RAM.
**Solution:** This is a hardware limit. Close Chrome tabs or buy more RAM. The tool minimizes its own footprint (`h4_omni_debug.log` auto-prunes old lines) to help.

---

```ascii
_________ad88888888888888888a, 
________a88888"888888888888888888, 
______,8888"__"P8888888888888888888b, 
______d88_________`""P888888888888888, 
_____,8888b_______________""888888888888, 
_____d8P'''__,aa,______________""888888888b 
_____888bbdd888888ba,__,I_________"88888888, 
_____8888888888888888ba8"_________,8888888b 
____,888888888888888888b,________,8888888888 
____(88888888888888888888,______,88888888888, 
____d888888888888888888888,____,8___"888888b 
____88888888888888888888888__.;8'"""__(888888 
____8888888888888I"8888888P_,8"_,aaa,__888888            (b'.')b - h4 - {Be Your Best}
____888888888888I:8888888"_,8"__`b8d'__(88888 
____(8888888888I'888888P'_,8)__________888088 
_____88888888I"__8888P'__,8")__________880888 
_____8888888I'___888"___,8"_(._.)_______808888 
_____(8888I"_____"88,__,8"_____________,8888P 
______888I'_______"P8_,8"_____________,88808) 
_____(88I'__________",8"__M""""""M___,8888988' 
____,8I"____________,8(____"aaaa"___,888888 
___,8I'____________,888a___________,888888) 
__,8I'____________,888888,_______,888888888 
_,8I'____________,8888888'`-===-'888888888' 
,8I'____________,8888888"________88888888" 
8I'____________,8"____88_________"888888P 
8I____________,8'_____88__________`P888" 
8I___________,8I______88____________"8ba,. 
(8,_________,8P'______88______________88""8bma,. 
_8I________,8P'_______88,______________"8b___""P8ma, 
_(8,______,8d"________`88,_______________"8b_____`"8a 
__8I_____,8dP_________,8X8,________________"8b.____:8b 
__(8____,8dP'__,I____,8XXX8,________________`88,____8) 
___8,___8dP'__,I____,8XxxxX8,_____I,_________8X8,__,8 
___8I___8P'__,I____,8XxxxxxX8,_____I,________`8X88,I8 
___I8,__"___,I____,8XxxxxxxxX8b,____I,________8XXX88I, 
___`8I______I'__,8XxxxxxxxxxxxXX8____I________8XXxxXX8, 
____8I_____(8__,8XxxxxxxxxxxxxxxX8___I________8XxxxxxXX8, 
___,8I_____I[_,8XxxxxxxxxxxxxxxxxX8__8________8XxxxxxxxX8, 
___d8I,____I[_8XxxxxxxxxxxxxxxxxxX8b_8_______(8XxxxxxxxxX8, 
___888I____`8,8Xxxxxxxxxh4xxxxxxxxX8_8,_____,8XxxxxxxxxxxX8 
___8888,____"88XxxxxxxxxxxxxxxxxxxX8)8I____.8XxxxxxxxxxxxX8 
__,8888I_____88XxxxxxxxxxxxxxxxxxxX8_`8,__,8XxxxxxxxxxxxX8" 
__d88888_____`8XXxxxxxxxxxxxxxxxxX8'__`8,,8XxxxxxxxxxxxX8" 
__888888I_____`8XXxxxxxxxxxxxxxxX8'____"88XxxxxxxxxxxxX8" 
__88888888bbaaaa88XXxxxxxxxxxxXX8)______)8XXxxxxxxXX8" 
__8888888I,_``""""""8888888888888888aaaaa8888XxxxxXX8" 
__(8888888I,______________________.__```"""""88888P" 
___88888888I,___________________,8I___8,_______I8" 
____"""88888I,________________,8I'____"I8,____;8" 
___________`8I,_____________,8I'_______`I8,___8) 
____________`8I,___________,8I'__________I8__:8' 
_____________`8I,_________,8I'___________I8__:8 
______________`8I_______,8I'_____________`8__(8 
_______________8I_____,8I'________________8__(8; 
_______________8I____,8"__________________I___88, 
______________.8I___,8'_______________________8"8, 
______________(PI___'8_______________________,8,`8, 
_____________.88'____________,_@___________.a8X8,`8, 
_____________(88____________@@@_________,a8XX88,`8, 
____________(888______________@'_______,d8XX8"__"b_`8, 
___________.8888,_____________________a8XXX8"____"a__`8, 
__________.888X88___________________,d8XX8I"______9,__`8, 
_________.88:8XX8,_________________a8XxX8I'_______`8___`8, 
________.88'_8XxX8a_____________,ad8XxX8I'________,8_____`8, 
________d8'__8XxxxX8ba,______,ad8XxxX8I"__________8___,___`8, 
_______(8I___8XxxxxxX888888888XxxxX8I"___________8___II___`8 
_______8I'___"8XxxxxxxxxxxxxxxxxxX8I'____________(8___8)____8; 
______(8I_____8XxxxxxxxxxxxxxxxxX8"_____________(8___8)____8I 
______8P'_____(8XxxxxxxxxxxxxxX8I'________________8,__(8____:8 
_____(8'_______8XxxxxxxxxxxxxxX8'_________________`8,_8_____8 
_____8I________`8XxxxxxxxxxxxX8'___________________`8,8___;8 
_____8'_________`8XxxxxxxxxxX8'_____________________`8I__,8' 
_____8___________`8XxxxxxxxX8'_______________________8'_,8' 
_____8____________`8XxxxxxX8'________________________8_,8' 
_____8_____________`8XxxxX8'________________________d'_8' 
_____8______________`8XxxX8_________________________8_8' 
_____8________________"8X8'_________________________"8" 
_____8,________________`88___________________________8 
_____8I________________,8'__________________________d) 
_____`8,_______________d8__________________________,8 
______(b_______________8'_________________________,8' 
_______8,_____________dP_________________________,8' 
_______(b_____________8'________________________,8' 
________8,___________d8________________________,8' 
________(b___________8'_______________________,8' 
_________8,_________a8_______________________,8' 
_________(b_________8'______________________,8' 
__________8,_______,8______________________,8' 
__________(b_______8'_____________________,8' 
___________8,_____,8_____________________,8' 
___________(b_____8'____________________,8' 
____________8,___d8____________________,8' 
____________(b__,8'___________________,8' 
_____________8,,I8___________________,8' 
_____________I8I8'__________________,8' 
_____________`I8I__________________,8' 
______________I8'_________________,8' 
______________"8_________________,8' 
______________(8________________,8' 
______________8I_______________,8' 
______________(b,___8,________,8) 
______________`8I___"88______,8i8, 
_______________(b,__________,8"8") 
_______________`8I__,8______8)_8_8 
________________8I__8I______"__8_8 
________________(b__8I_________8_8 
________________`8__(8,________b_8, 
_________________8___8)________"b"8, 
_________________8___8(_________"b"8 
_________________8___"I__________"b8, 
_________________8________________`8) 
_________________8_________________I8 
_________________8_________________(8 
_________________8,_________________8, 
_________________Ib_________________8) 
_________________(8_________________I8 
__________________8_________________I8 
__________________8_________________I8 
__________________8,________________I8 
__________________Ib________________8I 
__________________(8_______________(8' 
___________________8_______________I8 
___________________8,______________8I 
___________________Ib_____________(8' 
___________________(8_____________I8 
___________________`8_____________8I 
____________________8____________(8' 
____________________8,___________I8 
____________________Ib___________8I 
____________________(8___________8' 
_____________________8,_________(8 
_____________________Ib_________I8 
_____________________(8_________8I 
______________________8,________8' 
______________________(b_______(8 
_______________________8,______I8 
_______________________I8______I8 
_______________________(8______I8 
________________________8______I8, 
________________________8______8_8, 
________________________8,_____8_8' 
_______________________,I8_____"8" 
______________________,8"8,_____8, 
_____________________,8'_`8_____`b 
____________________,8'___8______8, 
___________________,8'____(a_____`b 
__________________,8'_____`8______8, 
__________________I8/______8______`b, 
__________________I8-/_____8_______`8, 
__________________(8/-/____8________`8, 
___________________8I/-/__,8_________`8 
___________________`8I/--,I8________-8) 
____________________`8I,,d8I_______-8) 
______________________"bdI"8,_____-I8 
___________________________`8,___-I8' 
____________________________`8,,--I8 
_____________________________`Ib,,I8 
______________________________`I8I
```