---
name: korean-coach
description: "Generate the operator's Korean lesson into the Obsidian vault — a 30-min business-track lesson (default), a 15-min review session, or the Friday weekly review. Use when the user says /korean-coach, 'korean lesson', or a Hermes cron invokes it headlessly. Args: '30' (default), '15', 'friday', or 'mine <sentence>'. Beginner→business-proficiency track, NIKL-graded verified corpus, hangul from day one with fast romanization wean, speech-level (honorific) discipline, spaced-repetition flashcards, adaptive difficulty from weekly self-test scores. Never asks questions in headless runs."
metadata:
  short-description: Adaptive Korean lesson generator → Obsidian; NIKL-graded corpus, honorific-first, business track
---

# Korean Coach

Follow `/opt/agentic/shared/skills/language-coach-core/CORE.md` for the engine: principles, vault
layout, state schemas, session recipes (30/15/Friday/checkpoint), story rules, anticipation drill,
corrections loop, flashcard format, mine mode, dashboard, and headless rules. This file adds only
what is Korean-specific. Read CORE.md first, every run.

Vault target: `<vault>/Agentic Output/languages/korean/`.

## Corpus (all under `data/` in this skill directory)

- `words/levelA.json` (960) / `levelB.json` (2,032) / `levelC.json` (2,490) — the official NIKL
  learner vocabulary joined with Wiktionary: `{"w","rr","ipa","pron","pos","hanja","en","rank","grade"}`.
  **`rr` is verbatim and must be copied, never re-derived, for any lemma.** `pron` gives the
  standard *pronounced* hangul when sound changes make it differ from spelling (일하다 → [일(ː)하다],
  회의 → [훼(ː)의]) — teach from it; it is the sound-change ground truth.
- `grammar/particles-endings.json` — curated closed-class morphemes (particles, verb endings) with
  RR and allomorph rules. Particles/endings are taught from THIS file, not the word lists (NIKL
  lists lemmas; single-syllable particles collide with homographs like 은 "silver").
- `grammar/sequence.md` — curated sequence, one point per lesson from L5, stages A→D.
- `ATTRIBUTION.md` — licenses (KOGL-1 + CC BY-SA); keep intact.

### The lemma rule (Korean is agglutinative — unlike the other coaches)

Dictionary words are lemmas (하다, 있다); real sentences use conjugated forms (해요, 합니다,
있어요). Therefore:
1. Known-words tracks **lemmas** (plus particles/endings tracked as taught grammar, not words).
2. A sentence is corpus-compliant when every content word is an inflection of a known/new lemma
   built ONLY from endings already taught (or today's ending). An untaught ending is a new
   element under i+1, same as a new word.
3. **RR of inflected forms** is composed mechanically from the lemma's verbatim `rr` + the ending's
   `rr` from particles-endings.json, applying standard RR sound-change conventions — the one
   sanctioned departure from copy-only. (Romanization is dropped fast anyway; see staging.)
4. Fixed formulas (안녕하세요, 감사합니다) may be taught before their grammar arrives: present as
   formula, name the lemma (안녕하다, 감사하다) which enters known-words, decompose properly when
   the ending is taught.

## Level track

`profile.level_track` takes exactly the values `"levelA"` → `"levelB"` → `"levelC"` (matching the
word-file names; NIKL grades ≈ beginner/intermediate/advanced; business-proficient territory
begins mid-B with Stage C register work). Track advances at ~90% grade coverage + checkpoint
≥ 80% (some grade words are journalese the syllabus skips — list them in the checkpoint note).
Coverage counts each distinct surface form once, even where the corpus holds multiple rows
(POS/homograph splits like 저 ×3) — conservative by design.

**CEFR map (approximate):** levelA ≈ A1–A2 (≈ TOPIK I levels 1–2) · levelB ≈ B1–B2
(≈ TOPIK II levels 3–4; business-fluent territory from mid-B with Stage C register) ·
levelC ≈ C1 (≈ TOPIK II levels 5–6). TOPIK is sit-able external proof — name the matching
TOPIK level in syllabus.md and checkpoint mocks.

## Unit 0 — hangul bootstrap (lessons 1–4)

Hangul is learnable in days — the bootstrap is short and the romanization wean is the fastest of
the three languages.
1. **L1 Hangul I**: syllable-block principle; basic consonants ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎ + vowels
   ㅏㅓㅗㅜㅡㅣㅐㅔ; reading CV syllables and first real words.
2. **L2 Hangul II**: aspirated ㅋㅌㅍㅊ, tense ㄲㄸㅃㅆㅉ, y-/w- compound vowels; 받침 (final
   consonants) and the 7 final sounds.
3. **L3 Sound changes + numbers**: 연음 liaison, nasalization, tensification, ㅎ-weakening —
   taught from the corpus `pron` field; Sino-Korean numbers 1–100; reading practice.
4. **L4 First dialogue**: greetings + business self-introduction — 안녕하세요 / 저는 … 입니다 /
   감사합니다 / 안녕히 계세요 as formulas (lemma rule §4), bowing + business-card etiquette note.
Regular CORE.md recipe starts at L5; story premieres L5 (cast introduced in L4's "coming up").
Unit 0 lessons use the recipe minus revenge round, grammar point, and story; Corrections applies
from L2 onward. Until grammar exists (L1–4), production-block written tasks are hangul
reading/writing tasks (read hangul → write RR + meaning; hear/copy → write hangul) with answer
slots, so Corrections always has material. The revenge round's read-aloud requirement survives
Unit 0 by living in the production block (one hangul-only read-aloud line). Shadowing uses the
day's syllables/words until dialogues exist; the anticipation drill starts at L2 with read-aloud
cues. Bare drill syllables are phonology, exempt from corpus-only (CORE principle 5); letter
names (기역, 니은…) are metalanguage, taught as script content. Checkpoints per CORE cadence:
L10, L20, … (Unit 0's content is gated inside the L10 checkpoint).

## Speech levels and honorifics are first-class (Korean's tones)

The register system is where Korean learners embarrass themselves, so it gets the discipline
tones get in the Mandarin/Thai coaches:
- **Every dialogue and model answer declares its speech level** (해요체 / 합쇼체) in a one-line
  label, and never mixes levels within one speaker's turn unless code-switching is the point
  (then say so).
- 해요체 (polite informal) is the default from L5. 합쇼체 (formal) arrives early — Stage A
  point 13 — because first business meetings run on it. 반말 is recognition-only until Stage C.
- Honorific/humble vocabulary pairs (있다/계시다, 주다/드리다, 말/말씀) are taught as pairs with
  a "who outranks whom" note, from the corpus.
- Card types added to CORE rules: register cards ("meeting register for 고마워요::감사합니다 /
  고맙습니다") and sound-change cards ("pronounce 회의::[훼의]") while stage ≠ `none`.
- Each lesson's revenge round includes 1 read-aloud line (hangul only) until stage = `none`
  (Unit 0: see the production-block rule above).
- Corpus `pos` values are mostly English but some rows carry NIKL Korean abbreviations
  (보 = auxiliary); always gloss POS in English in vocab tables regardless of the raw value.

## Romanization staging (Revised Romanization — fastest wean of the three)

- `full` (Unit 0 only, L1–4): RR under every Korean line.
- `new-only` (L5–14): RR only on new lemmas and in vocab tables; dialogues hangul-only with RR
  in a collapsed callout.
- `none` (from L15, first checkpoint passed): RR in vocab tables only. Hangul is fully phonetic
  with the sound-change rules from L3; leaning on romanization past Unit 0 is the documented
  crutch. Never regress the stage.
- Shadow/drill parseable lines are hangul-only from L1 (TTS reads them), per the CORE drill format.

## Business register (operator decision 6C)

- Units 1–2 (post-bootstrap): survival + transactional — greetings/titles, numbers/prices
  (both systems), scheduling and time, directions/taxi, ordering/paying, phone/KakaoTalk basics
  (KakaoTalk, not WeChat/LINE, is the Korean default).
- Unit 3+: meetings (회의), appointments, office small talk, email frames (Stage C point 36
  pulls forward as templates when needed).
- From ~month 3 of Korean study, set `profile.business_domain = "guidant-ops"`: AI/automation
  consulting, client operations, proposals — vocabulary-constrained; Korean borrows English tech
  terms as loanwords (컴퓨터-style) — loanwords must come from the corpus or stay in Latin script
  with a note.
- Business-register sequencing cross-checked against the free official KSI Business Korean 1–2
  topic order (reference only — never reproduce its content; it is copyrighted).
- Cultural-savvy thread (one practical paragraph per unit, woven into the dialogue): bow +
  business-card exchange (two hands, read it, don't pocket it), age/rank and why Koreans ask your
  age, title-based address (부장님 not 당신), drinking etiquette (pour for others, turn away from
  seniors), 눈치 (reading the room), KakaoTalk vs email register — practical, no orientalist trivia.

## Korean LLM failure modes → conservative rules

1. **Register mixing**: the declared-speech-level rule above; model answers always match the
   declared level; honorific infix -(으)시- never applied to the speaker's own actions.
2. **Spacing (띄어쓰기)**: particles attach to the preceding word with no space; spacing follows
   corpus/standard forms — when unsure between two spacings, choose the corpus segmentation and
   flag uncertainty rather than guessing silently.
3. **Romanization drift**: lemma RR verbatim from corpus; inflected RR only by the lemma rule §3;
   RR never appears outside its staged positions.
4. **Homographs**: the corpus join is hanja-disambiguated; when teaching a word whose `en` gloss
   doesn't fit the scenario sense, check the other level files for the homograph entry before
   assuming — if absent, treat as corpus gap ("corpus gap: <concept>"), never free-translate.
5. **Textbook stiffness**: prefer the shorter natural form the grammar sequence licenses
   (계세요 over full sentences, fragment+요) — dialogue lines should sound like an office, not
   an exam transcript.

## Story, stages, and the arc (CORE principles 8–9 applied to Korean)

- **Story ramp**: episodes 150–300 hangul syllables on levelA track; 300–500 on levelB; 500–800
  on levelC. Seoul office setting, same recurring-cast rules as CORE.
- **External assignments begin** at the levelB track (≈A2): weekly italki/exchange session,
  monthly human pronunciation check (sound-change fluency + intonation), graded listening
  (Comprehensible Korean-style channels), one graded reader per month.
- **B1 boundary / demotion**: reaching the levelC track triggers the CORE principle-9 notice —
  native media + mining become the main input; lessons become the review spine.

## Invocation

- `/korean-coach` or `/korean-coach 30` → 30-minute lesson (or checkpoint per CORE cadence).
- `/korean-coach 15` → 15-minute review session.
- `/korean-coach friday` → write/extend this week's note in `weekly/` per CORE.md.
- `/korean-coach mine <sentence>` → wild-caught sentence intake per CORE.md mine mode (interactive
  only; lemma identification + RR verified against corpus — unverifiable parts flagged, not guessed).
- Headless cron (operator sets up Hermes): same args; CORE.md headless rules apply — idempotent,
  no questions, fail loudly rather than improvise.
