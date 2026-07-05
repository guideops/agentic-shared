---
name: shadcn-ui
description: Use when building or editing UI with shadcn/ui — the copy-in (not-a-dependency) component library built on Radix UI + Tailwind CSS for React/Next.js. Covers installing the CLI, adding components (button, dialog, form, data-table, sidebar, chart, etc.), theming with CSS variables, dark mode, the registry/MCP for discovering components, and blocks. Use for React/Next/Vite/Remix/Astro projects that use Tailwind. Not for non-React stacks.
license: MIT
metadata:
  hermes:
    category: design
  source: https://github.com/shadcn-ui/ui
---

# shadcn/ui

shadcn/ui is **not an npm dependency** — you copy component source into your repo
and own it. Built on Radix UI primitives + Tailwind CSS. This skill is a usage
wrapper; the full library source is NOT vendored here (it is a 60MB+ monorepo).
Pull components on demand with the CLI instead.

## Init a project

```bash
npx shadcn@latest init
```
Prompts for style, base color, and CSS variables. Requires Tailwind already set up.

## Add components

```bash
npx shadcn@latest add button dialog form input card
npx shadcn@latest add data-table sidebar chart   # composite blocks
```
Components land in `components/ui/` and are yours to edit.

## Theming

- Colors are driven by CSS variables in `globals.css` (`--background`, `--primary`, …)
  mapped through `tailwind.config` / `@theme`.
- Dark mode: toggle the `.dark` class (e.g. via `next-themes`).
- Generate/browse themes at https://ui.shadcn.com/themes.

## Discovery (MCP)

shadcn ships an MCP server for searching components/blocks and pulling examples:

```bash
npx shadcn@latest mcp
```
The `ui-ux-pro-max` skill also integrates shadcn/ui MCP for component search.

## References

- Docs & component gallery: https://ui.shadcn.com
- Registry / blocks: https://ui.shadcn.com/blocks
- Source: https://github.com/shadcn-ui/ui
