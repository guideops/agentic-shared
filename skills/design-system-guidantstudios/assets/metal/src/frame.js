// dsx-metal: Guidant's liquid-silver frames for plain HTML (bundles React 18 + metal-fx).
import React from 'react';
import { createRoot } from 'react-dom/client';
import { MetalFx, MetalBadge, isMetalFxSupported, PRESETS, setSharedPresetMode } from 'metal-fx';
// Same tuning as guidantoperations.tech: silver, no red/blue dispersion (no gold fringes), cool tint.
setSharedPresetMode({ ...PRESETS.silver.modes.dark, colorTint: '#dbe7ff50', shiftRed: 0, shiftBlue: 0 });
window.React = window.React || React;
const h = React.createElement;
const theme = () => document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const listeners = new Set();
new MutationObserver(() => listeners.forEach(f => f())).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
function useTheme() { const [t, set] = React.useState(theme()); React.useEffect(() => { const f = () => set(theme()); listeners.add(f); return () => listeners.delete(f); }, []); return t; }
const Host = React.forwardRef(function Host({ el }, ref) {
  const own = React.useRef(null);
  React.useLayoutEffect(() => { if (own.current && el.parentNode !== own.current) own.current.appendChild(el); }, []);
  return h('span', { className: 'dsx-metal-host', ref: n => { own.current = n; if (n && el.parentNode !== n) n.appendChild(el); if (typeof ref === 'function') ref(n); else if (ref) ref.current = n; } });
});
function Frame({ el }) {
  const t = useTheme();
  const kind = el.getAttribute('data-metal');
  const r = parseFloat(getComputedStyle(el).borderTopLeftRadius) || 8;
  const strength = parseFloat(el.getAttribute('data-metal-strength')) || .72;
  return h(MetalFx, { preset: 'silver', variant: kind === 'circle' ? 'circle' : 'button', theme: t, strength, glowGain: .62,
    innerShadow: true, borderRadius: kind === 'circle' ? undefined : r, paused: reduced(), className: 'dsx-metal-frame' }, h(Host, { el }));
}
function mount(scope = document) {
  if (!isMetalFxSupported()) { document.documentElement.classList.add('dsx-metal-off'); return; }
  scope.querySelectorAll('[data-metal]:not([data-metal-mounted])').forEach(el => {
    el.setAttribute('data-metal-mounted', '');
    const holder = document.createElement('span'); holder.className = 'dsx-metal';
    el.parentNode.insertBefore(holder, el);
    createRoot(holder).render(h(Frame, { el }));
  });
  document.documentElement.classList.add('dsx-metal-on');
}
window.DSXMetal = { mount, isSupported: isMetalFxSupported, MetalFx, MetalBadge, React, createRoot };
const go = () => (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => mount());
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
