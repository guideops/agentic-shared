// dsx-metal-text: Guidant's chromatic liquid-metal headline accents for plain HTML. Load AFTER dsx-metal.js.
import { MetalText, isMetalFxSupported, PRESETS, setSharedPresetMode } from 'metal-fx';
const React = window.React, h = React.createElement;
if (isMetalFxSupported()) setSharedPresetMode({ ...PRESETS.chromatic.modes.dark, speed: .7, colorTint: '#b8d7ff40', shiftRed: .65, shiftBlue: .7, softness: .12 });
const theme = () => document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
function Txt({ text }) {
  const [t, set] = React.useState(theme());
  React.useEffect(() => { const mo = new MutationObserver(() => set(theme())); mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] }); return () => mo.disconnect(); }, []);
  return h(MetalText, { font: 'inherit', color: t === 'light' ? '#8594a4' : '#c6d3e6', theme: t, strength: 1, metalOpacity: 1, shaderScale: 2.2, innerShadow: null, className: 'dsx-metal-glyphs' }, text);
}
function mount(scope = document) {
  if (!isMetalFxSupported() || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  scope.querySelectorAll('[data-metal-text]:not([data-metal-mounted])').forEach(el => {
    el.setAttribute('data-metal-mounted', '');
    const text = el.textContent; el.textContent = ''; el.style.letterSpacing = '0';
    window.DSXMetal.createRoot(el).render(h(Txt, { text }));
  });
}
window.DSXMetalText = { mount };
const go = () => (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => mount());
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
