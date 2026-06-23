---
name: nextjs-scaffold
description: "Scaffold Next.js 14+ App Router components, pages, API routes, and full features. Follows project conventions. Outputs to current working directory or specified path."
metadata:
  hermes:
    category: app-dev
---

# nextjs-scaffold

**Trigger**: `/nextjs-scaffold <component|page|api|feature>` or "scaffold a Next.js", "create component", "new page"
**Domain**: app-dev
**Automation**: local (on-demand)

## Description
Scaffold Next.js 14+ App Router components, pages, API routes, and full features. Follows project conventions. Outputs to current working directory or specified path.

## Instructions
1. Accept scaffold type + name: `component Button`, `page /dashboard`, `api /users`, `feature auth`.
2. Detect project conventions:
   - Read `tsconfig.json`, `package.json` for aliases and dependencies.
   - Check if Tailwind, shadcn/ui, Prisma, NextAuth are present.
3. Generate appropriate files:
   - **component**: `components/<name>.tsx` with types, props interface, Tailwind classes.
   - **page**: `app/<route>/page.tsx` + optional `layout.tsx`, `loading.tsx`, `error.tsx`.
   - **api route**: `app/api/<route>/route.ts` with GET/POST handlers, Zod validation.
   - **feature**: all of the above + types, hooks, utils.
4. If shadcn/ui present → use shadcn primitives (Button, Card, Input, etc.).
5. Add PWA-safe patterns: no `window` access without `typeof window !== 'undefined'` guard.
6. Output files and show diff summary.
7. Log to `domains/app-dev/learnings.md`.

## Input
`/nextjs-scaffold component UserCard --props "name:string, avatar:string, role:UserRole"`
`/nextjs-scaffold page /dashboard/analytics`
`/nextjs-scaffold feature auth --provider github`

## Output
Generated files in project structure. Preview shown before writing (ask confirmation).

## Automation
None — on-demand only.
