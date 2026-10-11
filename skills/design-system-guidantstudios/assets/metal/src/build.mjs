import { build } from 'esbuild';
import { readFile } from 'node:fs/promises';
const patch = { name: 'metal-text-resize-fix', setup(b) { b.onLoad({ filter: /metal-fx[\\/]dist[\\/]index\.es\.js$/ }, async a => {
  let s = await readFile(a.path, 'utf8'); const before = 'e.relocNextIdx = t.relocNextIdx';
  if (s.split(before).length !== 2) throw new Error('resize patch anchor not found');
  s = s.replace(before, 'e.relocNextIdx = t.relocNextIdx < 0 ? t.relocNextIdx : Math.min(t.relocNextIdx, Math.max(0, e.perim.length - 1))');
  return { contents: s, loader: 'js' }; }); } };
const reactGlobal = { name: 'react-global', setup(b) {
  b.onResolve({ filter: /^react$/ }, () => ({ path: 'react', namespace: 'rg' }));
  b.onResolve({ filter: /^react\/jsx-runtime$/ }, () => ({ path: 'jsx', namespace: 'rg' }));
  b.onLoad({ filter: /^react$/, namespace: 'rg' }, () => ({ contents: 'module.exports = window.React;', loader: 'js' }));
  b.onLoad({ filter: /^jsx$/, namespace: 'rg' }, () => ({ contents: 'const R=window.React;export const Fragment=R.Fragment;export function jsx(t,p,k){return R.createElement(t,k==null?p:{...p,key:k})};export const jsxs=jsx;export const jsxDEV=jsx;', loader: 'js' })); } };
const common = { bundle: true, minify: true, format: 'iife', platform: 'browser', target: ['es2020'], define: { 'process.env.NODE_ENV': '"production"' }, legalComments: 'none' };
const banner = { js: '/* dsx-metal | metal-fx 2.0.11 (MIT, Jakub Antalik) incl. Paper Shaders liquidMetal (Apache-2.0, Paper Design) | React 18.3.1 (MIT, Meta) */' };
await build({ ...common, entryPoints: ['src/frame.js'], outfile: 'out/dsx-metal.js', plugins: [patch], banner });
await build({ ...common, entryPoints: ['src/text.js'], outfile: 'out/dsx-metal-text.js', plugins: [patch, reactGlobal], banner: { js: '/* dsx-metal-text | metal-fx 2.0.11 (MIT, Jakub Antalik) incl. Paper Shaders liquidMetal (Apache-2.0, Paper Design). Needs dsx-metal.js loaded first. */' } });
console.log('built');
