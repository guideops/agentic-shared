#!/usr/bin/env node
// generations skill — submit one fal.ai queue job, wait, save the result into the
// Generations folder with a JSON sidecar. Node 18+, no dependencies.
// Usage: node fal.mjs --endpoint <id> --name <base> --input '<json>'
//          [--ref <file>]... [--ref-field image_urls] [--out-dir <dir>] [--model <id>]
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'

function args(argv) {
  const out = { ref: [] }
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i]
    if (!k.startsWith('--')) throw new Error(`Unexpected argument: ${k}`)
    const key = k.slice(2), val = argv[++i]
    if (val === undefined) throw new Error(`Missing value for ${k}`)
    if (key === 'ref') out.ref.push(val); else out[key] = val
  }
  return out
}

function falKey() {
  if (process.env.FAL_KEY) return process.env.FAL_KEY.trim()
  const file = path.join(os.homedir(), '.config', 'generations', '.env')
  if (fs.existsSync(file)) {
    for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
      const m = line.match(/^\s*FAL_KEY\s*=\s*(.+?)\s*$/)
      if (m) return m[1].replace(/^["']|["']$/g, '')
    }
  }
  throw new Error('No FAL_KEY in the environment or ~/.config/generations/.env. Ask the operator to set it (Vaultwarden sync on the VPS); do not ask for it in chat.')
}

const MIME = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif' }

// Downscale big references to ≤1600px JPEG with ffmpeg when available; data
// URIs ride inside the request body, so smaller is faster.
function dataUri(file) {
  const ext = path.extname(file).toLowerCase()
  if (!MIME[ext]) throw new Error(`Reference must be an image: ${file}`)
  let buf = fs.readFileSync(file), mime = MIME[ext]
  if (buf.length > 1_500_000) {
    const tmp = path.join(os.tmpdir(), `gen-ref-${process.pid}-${Date.now()}.jpg`)
    try {
      execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', file, '-vf', "scale='min(1600,iw)':-2", '-q:v', '3', tmp])
      buf = fs.readFileSync(tmp); mime = 'image/jpeg'
    } catch { /* no ffmpeg: send the original */ } finally { try { fs.unlinkSync(tmp) } catch {} }
  }
  return `data:${mime};base64,${buf.toString('base64')}`
}

function outDir(explicit) {
  if (explicit) return path.resolve(explicit)
  const root = process.env.HERMES_DOCS_DIR || path.join(os.homedir(), 'Documents', 'Hermes')
  return path.join(root, 'generations')
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

async function falFetch(url, key, init = {}) {
  const r = await fetch(url, { ...init, headers: { Authorization: `Key ${key}`, 'Content-Type': 'application/json', ...(init.headers || {}) } })
  const text = await r.text()
  let body; try { body = JSON.parse(text) } catch { body = text }
  if (!r.ok) throw new Error(`fal ${r.status}: ${typeof body === 'string' ? body.slice(0, 400) : JSON.stringify(body.detail ?? body).slice(0, 400)}`)
  return body
}

function mediaUrls(result) {
  const urls = []
  for (const im of result.images || []) if (im?.url) urls.push(im.url)
  if (result.image?.url) urls.push(result.image.url)
  if (result.video?.url) urls.push(result.video.url)
  for (const v of result.videos || []) if (v?.url) urls.push(v.url)
  return urls
}

function extFor(url, contentType) {
  const fromType = { 'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp', 'image/gif': '.gif', 'video/mp4': '.mp4', 'video/webm': '.webm', 'video/quicktime': '.mov' }[String(contentType).split(';')[0]]
  if (fromType) return fromType
  const m = new URL(url).pathname.match(/\.(png|jpe?g|webp|gif|mp4|webm|mov)$/i)
  return m ? `.${m[1].toLowerCase().replace('jpeg', 'jpg')}` : '.bin'
}

function freeName(dir, base, ext) {
  let name = `${base}${ext}`, n = 1
  while (fs.existsSync(path.join(dir, name))) name = `${base}-${++n}${ext}`
  return name
}

async function main() {
  const a = args(process.argv.slice(2))
  if (!a.endpoint || !a.name || !a.input) throw new Error('Required: --endpoint, --name, --input')
  if (!/^[a-z0-9][a-z0-9_.\-/]*$/i.test(a.endpoint) || a.endpoint.includes('..')) throw new Error('Invalid endpoint id')
  const base = a.name.replace(/[^a-z0-9_.-]/gi, '_').slice(0, 120)
  const input = JSON.parse(a.input)
  const shown = JSON.parse(JSON.stringify(input))
  if (a.ref.length) {
    const field = a['ref-field'] || 'image_urls'
    const uris = a.ref.map((f) => dataUri(path.resolve(f)))
    input[field] = /urls$/.test(field) ? uris : uris[0]
    shown[field] = a.ref.map((f) => path.resolve(f))
  }
  const key = falKey()
  const dir = outDir(a['out-dir'])
  fs.mkdirSync(dir, { recursive: true })

  const sub = await falFetch(`https://queue.fal.run/${a.endpoint}`, key, { method: 'POST', body: JSON.stringify(input) })
  console.log(`submitted ${a.endpoint} request ${sub.request_id}`)
  const deadline = Date.now() + 20 * 60_000
  let last = ''
  for (;;) {
    if (Date.now() > deadline) throw new Error(`Timed out; request ${sub.request_id} may still finish. Status: ${sub.status_url}`)
    const st = await falFetch(sub.status_url, key)
    if (st.status !== last) { console.log(`status ${st.status}${st.queue_position != null ? ` (queue ${st.queue_position})` : ''}`); last = st.status }
    if (st.status === 'COMPLETED') { if (st.error) throw new Error(`fal failed: ${st.error_type || ''} ${st.error}`); break }
    await sleep(3000)
  }
  const result = await falFetch(sub.response_url, key)
  const urls = mediaUrls(result)
  if (!urls.length) throw new Error(`No media in result: ${JSON.stringify(result).slice(0, 400)}`)

  const saved = []
  for (const [i, url] of urls.entries()) {
    const r = await fetch(url)
    if (!r.ok) throw new Error(`Download failed (${r.status}) for ${url}`)
    const name = freeName(dir, urls.length > 1 ? `${base}_${i + 1}` : base, extFor(url, r.headers.get('content-type')))
    fs.writeFileSync(path.join(dir, name), Buffer.from(await r.arrayBuffer()))
    saved.push(name)
  }
  const sidecar = {
    prompt: input.prompt ?? null,
    model: a.model || null,
    endpoint: a.endpoint,
    input: shown,
    request_id: sub.request_id,
    files: saved,
    seed: result.seed ?? null,
    created: new Date().toISOString(),
  }
  fs.writeFileSync(path.join(dir, `${saved[0].replace(/\.[^.]+$/, '')}.json`), JSON.stringify(sidecar, null, 2) + '\n')
  for (const s of saved) console.log(`saved ${path.join(dir, s)}`)
}

main().catch((e) => { console.error(`error: ${e.message}`); process.exit(1) })
