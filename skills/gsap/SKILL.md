---
name: gsap
description: Use when building JavaScript/web animations with GSAP (GreenSock Animation Platform) — tweens, timelines, scroll-driven animation (ScrollTrigger), SVG/morph, text splitting (SplitText), Flip layout animation, draggable, and physics. Applies to any framework (vanilla JS, React via @gsap/react useGSAP, Vue, Svelte, Webflow). Use for scroll effects, hero/landing motion, sequenced UI choreography, and micro-interactions. Not for CSS-only transitions where GSAP is overkill.
license: "GSAP Standard (free, incl. all plugins as of 2025)"
metadata:
  hermes:
    category: design
  source: https://github.com/greensock/gsap
---

# GSAP — GreenSock Animation Platform

High-performance JS animation library. As of 2025 GSAP and **all** former "Club"
plugins (ScrollTrigger, SplitText, MorphSVG, Flip, Draggable, etc.) are **free**.
This skill is a usage wrapper; the library source is not vendored — install from npm.

## Install

```bash
npm install gsap
```

```js
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);
```

## Core API

```js
gsap.to(".box", { x: 200, rotation: 360, duration: 1, ease: "power2.out" });
gsap.from(".hero", { autoAlpha: 0, y: 40, stagger: 0.1 });

// Timeline: sequence + overlap with position params
const tl = gsap.timeline({ defaults: { duration: 0.6 } });
tl.to(".a", { x: 100 })
  .to(".b", { y: 50 }, "<")   // start with previous
  .to(".c", { opacity: 1 }, "-=0.2");
```

## Scroll-driven

```js
gsap.to(".panel", {
  xPercent: -100,
  scrollTrigger: { trigger: ".wrap", scrub: true, pin: true, end: "+=2000" },
});
```

## React

Use the official hook — handles cleanup and scoping:

```jsx
import { useGSAP } from "@gsap/react";       // npm i @gsap/react
useGSAP(() => { gsap.to(".box", { x: 100 }); }, { scope: containerRef });
```

## Key plugins

`ScrollTrigger` (scroll), `SplitText` (per-char/word text), `Flip` (layout state
transitions), `MorphSVG` (path morph), `Draggable`, `MotionPathPlugin`, `Observer`.
Register each with `gsap.registerPlugin(...)` before use.

## References

- Docs: https://gsap.com/docs/v3/
- Ease visualizer: https://gsap.com/docs/v3/Eases
- Source: https://github.com/greensock/gsap
