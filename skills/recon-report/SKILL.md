---
name: recon-report
description: "Structured recon and enumeration for authorized penetration tests. Runs passive and active recon phases, organizes findings, and outputs a professional report. Always requires scope confirmation before proceeding."
metadata:
  hermes:
    category: cybersecurity
---

# recon-report

**Trigger**: `/recon-report <target>` or "recon on", "reconnaissance report", "enumerate target"
**Domain**: cybersecurity
**Automation**: local (on-demand, authorized engagements only)

## Description
Structured recon and enumeration for authorized penetration tests. Runs passive and active recon phases, organizes findings, and outputs a professional report. Always requires scope confirmation before proceeding.

## Instructions

> **AUTHORIZATION CHECK**: Before any action, confirm: "Do you have written authorization to test <target>? (yes/no)". If no → stop.

1. Accept target (domain/IP/CIDR) + scope document or confirmation.
2. **Passive recon** (OSINT — no direct target contact):
   - WHOIS, DNS records (A, MX, TXT, NS, CNAME).
   - Subdomain enumeration via crt.sh, SecurityTrails (passive).
   - Google dorking suggestions (show commands, don't execute).
   - LinkedIn/GitHub employee/repo search.
   - Shodan/Censys (if user has API key in env).
3. **Active recon** (only within confirmed scope):
   - Port scan command generation (nmap): `nmap -sV -sC -O <target>` — show command, ask before run.
   - Web tech fingerprinting suggestions (Wappalyzer, whatweb).
   - Directory enumeration command (gobuster/ffuf).
4. Organize all findings into structured report.
5. Save to `domains/cybersecurity/engagements/<target>-YYYY-MM-DD/recon.md`.

## Input
`/recon-report example.com --scope "*.example.com, 192.168.1.0/24"`
Or interactive with scope prompts.

## Output
```markdown
---
domain: cybersecurity
date: YYYY-MM-DD
target: <target>
phase: recon
authorized: true
---
# Recon Report: <Target>
## Scope
## Passive Recon
### DNS / WHOIS
### Subdomains
### OSINT Findings
## Active Recon
### Open Ports
### Services
### Web Technologies
## Attack Surface Summary
## Recommended Next Steps
```

## Automation
None — manual, per-engagement only.
