---
name: self-audit
description: "Security audit of own Next.js/PWA projects before deployment. Covers OWASP Top 10, secrets detection, dependency vulnerabilities, and auth issues. No authorization needed — own code."
metadata:
  hermes:
    category: cybersecurity
---

# self-audit

**Trigger**: `/self-audit` or "audit my app", "security review", "check for vulnerabilities"
**Domain**: cybersecurity
**Automation**: local (pre-deploy hook)

## Description
Security audit of own Next.js/PWA projects before deployment. Covers OWASP Top 10, secrets detection, dependency vulnerabilities, and auth issues. No authorization needed — own code.

## Instructions
1. Scan codebase (run on cwd or `--path`):
   - **Secrets detection**: grep for hardcoded API keys, tokens, passwords, connection strings.
   - **Dependency audit**: run `npm audit` or `pnpm audit` — list high/critical CVEs.
   - **OWASP checks**:
     - A01 Broken Access Control: check API routes for missing auth middleware.
     - A02 Crypto Failures: check for MD5/SHA1 usage, HTTP (not HTTPS) endpoints.
     - A03 Injection: check for raw SQL queries, unsanitized user input in queries.
     - A05 Security Misconfiguration: check `next.config.js` for security headers.
     - A07 Auth Failures: check NextAuth config, JWT secrets, session handling.
   - **CSP**: verify Content-Security-Policy headers in `next.config.js`.
   - **CORS**: check API routes for overly permissive CORS.
   - **Rate limiting**: check if API routes have rate limiting (e.g., upstash/ratelimit).
2. Score each OWASP category: Pass / Warn / Fail.
3. Prioritize findings: Critical → High → Medium → Low.
4. Save audit report to `domains/cybersecurity/self-audits/YYYY-MM-DD-<project>.md`.
5. Log to `domains/cybersecurity/learnings.md`.

## Input
None (runs on cwd). Or `/self-audit --path ../my-nextjs-app`.

## Output
```markdown
# Security Audit — <Project> — YYYY-MM-DD
## Overall Risk: Medium
## Findings
| ID | Category | Severity | File | Line | Issue | Fix |
|----|----------|----------|------|------|-------|-----|
## Dependency Vulnerabilities
## Recommendations (Priority Order)
## Sign-off Checklist
```

## Automation
Local pre-deploy hook: add to `package.json`:
`"pre-deploy": "Codex --headless --project=. '/self-audit'"`.
Blocks deploy if Critical findings exist.
