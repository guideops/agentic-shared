---
name: pwa-audit
description: "Audit a Next.js/PWA project for PWA compliance, performance, and security before deployment. Outputs a scored report with pass/fail per check."
metadata:
  hermes:
    category: app-dev
---

# pwa-audit

**Trigger**: `/pwa-audit` or "audit my PWA", "check PWA compliance", "PWA checklist"
**Domain**: app-dev
**Automation**: local (pre-deploy hook)

## Description
Audit a Next.js/PWA project for PWA compliance, performance, and security before deployment. Outputs a scored report with pass/fail per check.

## Instructions
1. Scan project for PWA requirements:
   - `manifest.json` or `app/manifest.ts`: icons (192x192, 512x512), name, theme_color, start_url.
   - Service worker: registration in `layout.tsx` or `_app.tsx`, caching strategy.
   - HTTPS-only (check for hardcoded `http://` URLs).
   - Offline fallback page exists.
2. Next.js specific checks:
   - `next/image` used (not raw `<img>`).
   - No `window`/`document` without SSR guard.
   - `metadata` export in root `layout.tsx`.
   - Font optimization via `next/font`.
3. Security checks (OWASP basics):
   - No API keys in client components (`'use client'` files).
   - CSP headers in `next.config.js`.
   - `NEXTAUTH_SECRET` not hardcoded.
4. Performance checks:
   - No large client bundles (flag files >50KB imported in client components).
   - Images have `width`/`height` or `fill`.
5. Score each category 0-100. Overall score = weighted average.
6. Save report to `domains/app-dev/audits/YYYY-MM-DD-pwa-audit.md`.

## Input
None (runs on cwd). Or `/pwa-audit --path /other/project`.

## Output
```markdown
# PWA Audit — YYYY-MM-DD
## Score: 82/100
| Check | Status | Notes |
|-------|--------|-------|
| Manifest | ✅ | icons complete |
| Service Worker | ⚠️ | no offline fallback |
| HTTPS | ✅ | |
| CSP Headers | ❌ | missing in next.config.js |
## Recommendations
```

## Automation
Local pre-deploy: add to `package.json` scripts as `"pre-deploy": "Codex --headless --project=. '/pwa-audit'"`.
