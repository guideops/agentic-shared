---
name: ctf-assist
description: "CTF challenge assistant. Helps with hints, methodology, tooling, and writeup generation. Supports web, crypto, reverse engineering, forensics, pwn, and OSINT categories."
metadata:
  hermes:
    category: cybersecurity
---

# ctf-assist

**Trigger**: `/ctf-assist <challenge description or file>` or "help with CTF", "CTF challenge", "solve this flag"
**Domain**: cybersecurity
**Automation**: local (on-demand)

## Description
CTF challenge assistant. Helps with hints, methodology, tooling, and writeup generation. Supports web, crypto, reverse engineering, forensics, pwn, and OSINT categories.

## Instructions
1. Accept challenge description, category, and any provided files.
2. Identify category (web, crypto, rev, forensics, pwn, misc, OSINT).
3. Apply category-specific methodology:
   - **Web**: Check cookies, source, robots.txt, SQLi, XSS, IDOR, SSRF, XXE, JWT issues.
   - **Crypto**: Identify cipher (Caesar, XOR, RSA, AES modes), suggest attack (frequency analysis, weak key, padding oracle).
   - **Rev**: Suggest tools (Ghidra, strings, ltrace, strace, Cutter). Walk through static analysis steps.
   - **Forensics**: Check file magic bytes, steganography (steghide, binwalk, strings), metadata, pcap analysis.
   - **Pwn**: Check binary protections (checksec), identify overflow/format string, suggest exploit approach.
   - **OSINT**: Reverse image search, username search, geolocation, metadata.
4. Give hints progressively (don't immediately give the flag).
5. If user has flag → generate writeup and save to `domains/cybersecurity/ctf/YYYY-MM-DD-<challenge>.md`.
6. Log to `domains/cybersecurity/learnings.md` with skills learned.

## Input
`/ctf-assist "Base64 encoded string: SGVsbG8gV29ybGQ=" --category crypto`
Or paste challenge description interactively.

## Output
Structured hints + tool commands. Writeup saved to:
`domains/cybersecurity/ctf/YYYY-MM-DD-<challenge-name>.md`

## Automation
None — on-demand per challenge.
