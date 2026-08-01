#!/usr/bin/env node
// Insights recon fetcher — daily AI-news sweep for guidantoperations.tech "Insights".
// Zero deps (Node 18+ global fetch). Every source failure is non-fatal and reported.
//
// Output: <data-dir>/raw-YYYY-MM-DD.json  { date, fetchedAt, errors, urgentCandidates, stories[] }
// State:  <data-dir>/seen.json            { url: firstSeenISO } (21-day window)
//
// <data-dir> = $INSIGHTS_DATA_DIR, else ~/.insights — machine-portable so the
// same skill runs on the laptop and the VPS without path edits.
//
// Usage: node insights-recon.mjs [--date YYYY-MM-DD] [--fresh-hours N]

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const OUT_DIR = process.env.INSIGHTS_DATA_DIR || path.join(os.homedir(), '.insights');
const SEEN_FILE = path.join(OUT_DIR, 'seen.json');
const SEEN_WINDOW_DAYS = 21;
const PER_SOURCE_CAP = 12;
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) insights-recon/1.0';

const args = process.argv.slice(2);
const argVal = (flag, dflt) => {
  const i = args.indexOf(flag);
  return i >= 0 && args[i + 1] ? args[i + 1] : dflt;
};
const localDate = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};
const DATE = argVal('--date', localDate());
const FRESH_HOURS = Number(argVal('--fresh-hours', '48'));

// ── Sources ──────────────────────────────────────────────────────────────────
// tier: primary (vendor), curator (high-signal individuals/newsletters),
//       aggregate (curated digests), social (community pulse), ship (releases)
const SOURCES = [
  { id: 'openai',     tier: 'primary', type: 'rss',  url: 'https://openai.com/news/rss.xml' },
  { id: 'deepmind',   tier: 'primary', type: 'rss',  url: 'https://deepmind.google/blog/rss.xml' },
  { id: 'google-ai',  tier: 'primary', type: 'rss',  url: 'https://blog.google/technology/ai/rss/' },
  { id: 'mistral',    tier: 'primary', type: 'rss',  url: 'https://mistral.ai/rss.xml' },
  { id: 'anthropic',  tier: 'primary', type: 'anthropic-news', url: 'https://www.anthropic.com/news' },
  { id: 'willison',   tier: 'curator', type: 'rss',  url: 'https://simonwillison.net/atom/everything/' },
  { id: 'import-ai',  tier: 'curator', type: 'rss',  url: 'https://importai.substack.com/feed' },
  { id: 'smol-ai',    tier: 'aggregate', type: 'rss', url: 'https://news.smol.ai/rss.xml' },
  { id: 'tldr-ai',    tier: 'aggregate', type: 'rss', url: 'https://tldr.tech/api/rss/ai' },
  { id: 'hn-front',   tier: 'social',  type: 'hn-algolia', url: 'https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=25' },
  { id: 'hf-blog',    tier: 'ship',    type: 'rss',  url: 'https://huggingface.co/blog/feed.xml' },
  { id: 'hf-trending',tier: 'ship',    type: 'hf-trending', url: 'https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=10' },
  { id: 'gh-trending',tier: 'ship',    type: 'gh-trending', url: 'https://github.com/trending?since=daily' },
];

// ── Helpers ──────────────────────────────────────────────────────────────────
async function get(url, accept) {
  const res = await fetch(url, {
    headers: { 'user-agent': UA, ...(accept ? { accept } : {}) },
    redirect: 'follow',
    signal: AbortSignal.timeout(20000),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.text();
}

const strip = (s) =>
  String(s || '')
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'").replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

const tag = (xml, name) => {
  const m = xml.match(new RegExp(`<${name}[^>]*>([\\s\\S]*?)</${name}>`, 'i'));
  return m ? m[1] : '';
};

// RSS 2.0 <item> and Atom <entry>
function parseFeed(xml) {
  const items = [];
  const blocks = xml.match(/<item[\s>][\s\S]*?<\/item>/gi) || xml.match(/<entry[\s>][\s\S]*?<\/entry>/gi) || [];
  for (const b of blocks) {
    let link = strip(tag(b, 'link'));
    if (!link) {
      // Atom: <link href="..."/> — prefer rel="alternate" or first href
      const alt = b.match(/<link[^>]*rel=["']alternate["'][^>]*href=["']([^"']+)["']/i) || b.match(/<link[^>]*href=["']([^"']+)["']/i);
      link = alt ? alt[1] : '';
    }
    const date = strip(tag(b, 'pubDate')) || strip(tag(b, 'published')) || strip(tag(b, 'updated')) || strip(tag(b, 'dc:date'));
    items.push({
      title: strip(tag(b, 'title')),
      url: link,
      publishedAt: date ? new Date(date).toISOString() : null,
      summary: strip(tag(b, 'description') || tag(b, 'summary') || tag(b, 'content')).slice(0, 400),
    });
  }
  return items.filter((i) => i.title && i.url);
}

// Anthropic has no RSS — scrape /news for article links.
function parseAnthropicNews(html) {
  const items = [];
  const seen = new Set();
  const re = /href="(\/news\/[a-z0-9-]+)"[^>]*>([\s\S]*?)<\/a>/gi;
  let m;
  while ((m = re.exec(html))) {
    const url = `https://www.anthropic.com${m[1]}`;
    if (seen.has(url)) continue;
    seen.add(url);
    const title = strip(m[2]).slice(0, 200);
    if (title.length > 8) items.push({ title, url, publishedAt: null, summary: '' });
  }
  return items;
}

function parseHfTrending(json) {
  return (JSON.parse(json) || []).map((mdl) => ({
    title: `HF trending: ${mdl.id}`,
    url: `https://huggingface.co/${mdl.id}`,
    publishedAt: mdl.lastModified || null,
    summary: `↓${mdl.downloads ?? '?'} ♥${mdl.likes ?? '?'} ${mdl.pipeline_tag || ''}`.trim(),
  }));
}

function parseHnAlgolia(json) {
  return (JSON.parse(json).hits || []).map((h) => ({
    title: h.title || '',
    url: h.url || `https://news.ycombinator.com/item?id=${h.objectID}`,
    publishedAt: h.created_at || null,
    points: h.points ?? 0,
    comments: h.num_comments ?? 0,
    summary: `${h.points ?? 0} points, ${h.num_comments ?? 0} comments — https://news.ycombinator.com/item?id=${h.objectID}`,
  })).filter((i) => i.title);
}

function parseGhTrending(html) {
  const items = [];
  const seen = new Set();
  const re = /<h2[^>]*class="[^"]*lh-condensed[^"]*"[^>]*>[\s\S]*?<a[^>]*href="\/([^"\/]+\/[^"\/]+)"/gi;
  let m;
  while ((m = re.exec(html))) {
    const repo = m[1];
    if (seen.has(repo)) continue;
    seen.add(repo);
    items.push({ title: `GH trending: ${repo}`, url: `https://github.com/${repo}`, publishedAt: null, summary: '' });
  }
  return items;
}

// ── Main ─────────────────────────────────────────────────────────────────────
fs.mkdirSync(OUT_DIR, { recursive: true });

let seen = {};
try { seen = JSON.parse(fs.readFileSync(SEEN_FILE, 'utf8')); } catch { /* first run */ }
const cutoffSeen = Date.now() - SEEN_WINDOW_DAYS * 864e5;
for (const [url, iso] of Object.entries(seen)) {
  if (new Date(iso).getTime() < cutoffSeen) delete seen[url];
}

const freshCutoff = Date.now() - FRESH_HOURS * 36e5;
const errors = {};
const stories = [];

const results = await Promise.allSettled(
  SOURCES.map(async (src) => {
    const body = await get(src.url, src.type === 'rss' ? 'application/rss+xml, application/atom+xml, text/xml' : undefined);
    let items;
    if (src.type === 'rss') items = parseFeed(body);
    else if (src.type === 'anthropic-news') items = parseAnthropicNews(body);
    else if (src.type === 'hf-trending') items = parseHfTrending(body);
    else if (src.type === 'hn-algolia') items = parseHnAlgolia(body);
    else if (src.type === 'gh-trending') items = parseGhTrending(body);
    else items = [];
    return { src, items };
  }),
);

for (let i = 0; i < results.length; i++) {
  const src = SOURCES[i];
  const r = results[i];
  if (r.status === 'rejected') {
    errors[src.id] = String(r.reason?.message || r.reason);
    continue;
  }
  let kept = 0;
  for (const item of r.value.items) {
    if (kept >= PER_SOURCE_CAP) break;
    // Freshness: dated items must be recent; undated items pass if never seen.
    if (item.publishedAt && new Date(item.publishedAt).getTime() < freshCutoff) continue;
    const isNew = !seen[item.url];
    if (!isNew) continue;
    seen[item.url] = new Date().toISOString();
    stories.push({ source: src.id, tier: src.tier, ...item });
    kept++;
  }
}

// Cross-source overlap: same normalized title root seen from 2+ sources = strong candidate.
const norm = (t) => t.toLowerCase().replace(/[^a-z0-9 ]/g, '').split(/\s+/).filter((w) => w.length > 3).slice(0, 6).join(' ');
const byNorm = new Map();
for (const s of stories) {
  const k = norm(s.title);
  if (!k) continue;
  byNorm.set(k, (byNorm.get(k) || 0) + 1);
}
for (const s of stories) s.crossSourceHits = byNorm.get(norm(s.title)) || 1;

// Mechanical urgency gate (Plan: keep the flag rare). LLM step confirms or
// demotes each candidate with a one-line justification; it may also promote a
// primary-tier release/policy story the numbers can't see.
const urgentCandidates = stories
  .filter((s) => s.crossSourceHits >= 3 || (s.points || 0) >= 400)
  .map((s) => ({ url: s.url, title: s.title, reason: s.crossSourceHits >= 3 ? `${s.crossSourceHits} sources within window` : `HN ${s.points} points` }));

const out = {
  date: DATE,
  fetchedAt: new Date().toISOString(),
  freshHours: FRESH_HOURS,
  sources: SOURCES.map((s) => ({ id: s.id, tier: s.tier, ok: !errors[s.id] })),
  errors,
  count: stories.length,
  urgentCandidates,
  stories,
};

const outFile = path.join(OUT_DIR, `raw-${DATE}.json`);
fs.writeFileSync(outFile, JSON.stringify(out, null, 2));
fs.writeFileSync(SEEN_FILE, JSON.stringify(seen, null, 2));

console.log(`[insights-recon] ${DATE}: ${stories.length} new stories, ${urgentCandidates.length} urgent candidates, ${Object.keys(errors).length} source errors -> ${outFile}`);
for (const [id, msg] of Object.entries(errors)) console.log(`  ✕ ${id}: ${msg}`);
