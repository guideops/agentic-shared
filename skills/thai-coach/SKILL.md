---
name: thai-coach
description: "Generate the operator's Thai lesson into the Obsidian vault — a 30-min business-track lesson (default), a 15-min review session, or the Friday weekly review. Use when the user says /thai-coach, 'thai lesson', or a Hermes cron invokes it headlessly. Args: '30' (default), '15', 'friday', or 'mine <sentence>'. Beginner→business-proficiency track, frequency-tiered verified corpus, Thai script from day one with staged Paiboon romanization, spaced-repetition flashcards, adaptive difficulty from weekly self-test scores. Never asks questions in headless runs."
metadata:
  short-description: Adaptive Thai lesson generator → Obsidian; corpus-verified, script-first, business track
---

# Thai Coach

Follow `/opt/agentic/shared/skills/language-coach-core/CORE.md` for the engine: principles, vault
layout, state schemas, session recipes (30/15/Friday/checkpoint), story rules, anticipation drill,
corrections loop, flashcard format, mine mode, dashboard, and headless rules. This file adds only
what is Thai-specific. Read CORE.md first, every run.

Vault target: `<vault>/Agentic Output/languages/thai/`.

**Thai is the language where LLM free-generation is least reliable** (low-resource; documented
hallucinated vocab, wrong tones, mixed romanization schemes). The conservative rules below are
therefore stricter than the Mandarin skill's. When a rule here and convenience conflict, the rule
wins; when the corpus is silent, say so in the note rather than guessing.

## Corpus (all under `data/` in this skill directory)

- `words/tier1.json` … `tier4.json` — 3,500 words: Thai National Corpus frequency rank joined with
  Wiktionary data: `{"w","pb","rtgs","ipa","pos","en","rank"}`. **`pb` (Paiboon, tone-marked) is
  the taught romanization and must be copied verbatim — never reconstruct or re-derive it.** RTGS
  appears once per new word in the vocab table (it's what street signs use), never elsewhere.
- Gloss selection: `en` holds up to 3 dictionary senses in dictionary order, not learner order
  (คุณ lists "attribute" before "you"). Teach the sense that fits the lesson's context; the `en`
  field is the verified pool to choose from, not a forced primary meaning.
- Frequency-tier pull-forward: tiers order default teaching, but TNC is a written corpus and
  underranks speech essentials (สวัสดี is tier4). Any word from ANY tier may be pulled forward
  when the scenario needs it — all tiers are equally verified. Log pulled-forward words normally
  in known-words.
- `grammar/sequence.md` — curated sequence (Thai has no official L2 lists), one point per lesson
  from L9, stages A→D. Editable syllabus, not ground truth — improvements welcome, in the file.
- `ATTRIBUTION.md` — licenses (CC BY-SA on words/); keep intact.

## Level track

**CEFR map (self-defined — Thai has no official CEFR-mapped exam ladder; mark approximate
everywhere):** tier1 ≈ A1 · tier2 ≈ A2 · tier3 ≈ B1 · tier4 ≈ B2. The only formal external test
is CU-TFL (Chulalongkorn) — name it in syllabus.md as the optional proof point.

`profile.level_track` walks tier1 → tier2 → tier3 → tier4. Track advances when ~90% of the tier is
in known-words AND the latest checkpoint scored ≥ 80% (100% coverage is unreachable for a written
corpus — some tier words are journalese the syllabus legitimately skips; list skipped words in the
checkpoint note).

## Unit 0 — script and sound bootstrap (lessons 1–8)

Thai script carries the tone system, so the bootstrap is deliberately longer than Mandarin's.
Reading Thai is non-negotiable: transliteration-only Thai (the FSI-era approach) is lossy about
tones and caps out fast.

1. **L1 Sound system + the 5 tones**: mid/low/high/rising/falling with Paiboon tone marks and IPA
   contours from the corpus; the 9 mid-class consonants (ก จ ด ต บ ป อ ฎ ฏ) + long vowels า ี ู;
   first read syllables.
2. **L2 Live/dead syllables** + more vowels (เ- แ- โ- ไ- ใ-); reading practice with mid-class.
3. **L3 High-class consonants** (ข ฉ ถ ผ ฝ ส ห ศ ษ) + tone rules I (class × live/dead).
4. **L4 Low-class consonants** (the rest) + tone rules II; the full class×syllable tone chart.
5. **L5 Tone marks** ่ ้ ๊ ๋ over each class; completing the tone-derivation chart.
6. **L6 Remaining vowels** (short forms, ำ ัว เ-ือ เ-ีย ฤ), vowel shortening, final-consonant
   sounds (the 8 finals) and spelling-vs-sound.
7. **L7 Clusters, silent การันต์ marks, irregulars** (ทร, รร, ฯลฯ-class oddities); Thai numerals.
8. **L8 First dialogue**: greetings + self-introduction (business register: name, company, role);
   สวัสดี + polite particles + the wai (etiquette note).
**Checkpoint cadence override (Thai counts from the bootstrap):** checkpoints fire at L8, L18,
L28… — every 10 lessons anchored to the end of Unit 0, replacing CORE's `% 10` rule. The L8
checkpoint is the **script gate**: read-aloud lines, tone derivations, and the L8 dialogue; ≥ 80%
admits the regular recipe. Units after the bootstrap are 10 lessons each (Unit 1 = L9–18, …), so
every unit ends on its own checkpoint.

Regular CORE.md recipe starts at L9; the serialized story premieres at L9 (cast introduced in L8's
"coming up"). Unit 0 lessons use the recipe minus revenge round, grammar point, and story;
Corrections applies from L2 onward. The shadowing script uses the day's syllable drills/phrases
until dialogues exist. The anticipation drill starts at L2 with reading-aloud cues
(`EN: read: <Thai>` → pause → `TL:` answer) until there is enough vocabulary for production cues.
Bare drill syllables for tone/reading practice are phonology, exempt from corpus-only
(CORE principle 5) — but any *word* presented as a word must be corpus-verified.

## Tones and script are first-class

- Every new word: Thai script + Paiboon (verbatim from `pb`) + tone names on first appearance
  (ประชุม bprà-chum, low-mid). While `romanization_stage` = `full`, note WHY the tone is what it
  is (consonant class + syllable type + mark) for one word per lesson — the derivation is the
  skill Thai learners skip and regret.
- Each lesson's revenge round includes 1 read-aloud line (Thai script only) until stage = `none`;
  in Unit 0 (no revenge round) the read-aloud line lives in the production block instead.
- **Ear-preview words**: corpus words may appear as labeled listening/tone anchors ("previews for
  your ear, not today's vocabulary") without counting toward the 8-word cap or entering
  known-words — Unit 0's tone demonstrations need real contours before the letters that spell
  them are taught. Preview words must still be corpus entries with verbatim `pb`.
- **Consonant letter names** (ก ไก่ "chicken" style — how Thais spell aloud): metalanguage, not
  vocabulary. Introduce each letter's name as script content with the mnemonic word glossed; the
  mnemonic word joins known-words only if separately taught as a word.
- Tone-derivation cards and read-aloud cards are added to CORE card rules while stage ≠ `none`.

## Romanization staging (Paiboon)

- `full` (Unit 0 + Unit 1, lessons 1–16): Paiboon under every Thai line.
- `new-only` (L17+, if last checkpoint ≥ 80%): Paiboon only on new words and in vocab tables;
  everything else Thai script with Paiboon in a collapsed callout.
- `none` (when tier2 track reached): Paiboon in vocab tables only. Thai script is phonetic —
  wean fast; the script IS the pronunciation guide. Never regress the stage.
- The shadow/drill block parseable lines stay Thai-script-only (TTS reads them), per the CORE
  drill format; RTGS never appears outside vocab tables.

## Register, gender, and politeness

- Polite particles from L8 onward: every dialogue/model answer ends utterances with ครับ or ค่ะ/คะ
  as appropriate. `profile.speaker_gender` ("male" → ผม/ครับ, "female" → ฉัน(ดิฉัน)/ค่ะ+คะ) controls
  which form model answers and production targets use; until the operator sets it, teach and model
  BOTH forms side by side and note the field is unset on the dashboard.
- Kinship-term address (พี่/น้อง) and คุณ + name arrive per the grammar sequence (Stage C formal
  register), not ad hoc.
- Cultural-savvy thread (one practical etiquette paragraph per unit, woven into the dialogue):
  the wai and who initiates, hierarchy and age in address, กรงใจ (kreng jai) restraint in requests,
  business-card and meeting etiquette, Buddhism-adjacent taboos (head/feet, monks), royal-family
  respect (and the legal weight of it) — practical register guidance, no orientalist trivia.

## Business register (operator decision 6C)

- Units 1–2 (post-bootstrap): survival + transactional — greetings/titles, numbers/prices,
  scheduling and time, taxi/directions, ordering/paying, phone/LINE basics (LINE, not WeChat,
  is the Thai default).
- Unit 3+: meetings (ประชุม), appointments, office small talk, email/message frames.
- From ~month 3 of Thai study, set `profile.business_domain = "guidant-ops"`: AI/automation
  consulting, client operations, proposals — vocabulary-constrained; domain terms beyond the
  corpus enter as glossed loanwords (Thai borrows English tech terms heavily — คอมพิวเตอร์-style
  transliterations must come from the corpus or stay in Latin script with a note).
- **Honesty rule**: there is no business-Thai corpus anywhere. Stage C/D business scenarios are
  synthesized from verified vocabulary + the curated sequence. The dashboard external-assignments
  block must therefore start EARLIER than Mandarin's — from the tier2 track (≈A2): weekly
  italki/exchange session with a Thai tutor is the business-register ground truth this skill
  cannot provide.

## Story, stages, and the arc (CORE principles 8–9 applied to Thai)

- **Story ramp**: episodes 100–200 Thai characters on tier1 track; 200–400 on tier2; 400–600 on
  tier3+. Bangkok office setting, same recurring-cast rules as CORE.
- **External assignments begin** at tier2 (≈A2, earlier than Mandarin — see honesty rule): weekly
  tutor/exchange, monthly human tone check (tones AND vowel length — both phonemic, both inaudible
  to the speaker), graded listening (Comprehensible Thai-style channels).
- **B1 boundary / demotion**: reaching the tier3 track triggers the CORE principle-9 notice —
  native media + mining become the main input; lessons become the review spine.

## Thai LLM failure modes → conservative rules

1. **Hallucinated words**: corpus-only, no exceptions beyond CORE's glossed-proper-noun rule.
   A word not in any tier file may not be taught. If a scenario genuinely needs an absent word,
   write "corpus gap: <English concept>" in the note instead of inventing Thai.
2. **Wrong tones/romanization**: `pb` copied verbatim, always; never romanize a Thai *word*
   yourself, never mix schemes (RTGS only in its one vocab-table column). Sole exemption: bare
   phonology-drill syllables may be romanized by mechanical mapping from letter-sound values
   already taught, cross-checked against corpus `pb` for any grid cell that happens to be a real
   corpus string.
3. **Segmentation** (Thai writes without spaces): vocab items and drill lines segment exactly as
   corpus entries; dialogue lines add no spacing inside words. When quoting a multi-word phrase,
   its parts must each be corpus entries.
4. **Spelling drift**: any Thai string longer than one word must be assembled from verified
   corpus spellings — no from-memory spellings of untaught words, even in collapsed answers.

## Invocation

- `/thai-coach` or `/thai-coach 30` → 30-minute lesson (or checkpoint if lesson % 10 == 0).
- `/thai-coach 15` → 15-minute review session.
- `/thai-coach friday` → write/extend this week's note in `weekly/` per CORE.md.
- `/thai-coach mine <sentence>` → wild-caught sentence intake per CORE.md mine mode (interactive
  only; segmentation and Paiboon verified against corpus — unverifiable parts flagged, not guessed).
- Headless cron (operator sets up Hermes): same args; CORE.md headless rules apply — idempotent,
  no questions, fail loudly rather than improvise.
