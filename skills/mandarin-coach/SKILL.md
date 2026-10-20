---
name: mandarin-coach
description: "Generate the operator's Mandarin lesson into the Obsidian vault — a 30-min business-track lesson (default), a 15-min review session, or the Friday weekly review. Use when the user says /mandarin-coach, 'mandarin lesson', 'chinese lesson', or a Hermes cron invokes it headlessly. Args: '30' (default), '15', or 'friday'. Beginner→business-proficiency track, HSK 3.0-constrained vocabulary, spaced-repetition flashcards, adaptive difficulty from weekly self-test scores. Never asks questions in headless runs."
metadata:
  short-description: Adaptive Mandarin lesson generator → Obsidian; HSK 3.0-grounded, business track
---

# Mandarin Coach

Follow `/opt/agentic/shared/skills/language-coach-core/CORE.md` for the engine: principles, vault
layout, state schemas, session recipes (30/15/Friday/checkpoint), flashcard format, dashboard, and
headless rules. This file adds only what is Mandarin-specific. Read CORE.md first, every run.

Vault target: `<vault>/Agentic Output/languages/mandarin/`.

## Corpus (all under `data/` in this skill directory — never generate vocab outside it)

- `words/hsk1.json` … `hsk7-9.json` — HSK 3.0 (2025) words: `{"w","t","p","pos","en"}`
  (simplified, traditional-if-different, pinyin, POS, gloss). Level order = teaching order;
  within a level, prefer words that unlock the day's scenario.
- `grammar/hsk1.json` … — official HSK 3.0 grammar points per level; teach in listed order,
  one per lesson, explained in plain English with 3+ example sentences from known words.
- `bct/bcta_600.tsv`, `bct/bctb_4000.tsv` — Business Chinese Test vocabularies. When choosing
  among eligible HSK words, words that also appear in BCT(A) win — business relevance for free.
- `ATTRIBUTION.md` — licenses; keep intact.

## Level track

`profile.level_track` walks hsk1 → hsk2 → hsk3 → hsk4 → hsk5 (business-proficient territory begins
~hsk4 + BCT(B) coverage). Track advances when every word of the current level is in known-words AND
the latest checkpoint scored ≥ 80%.

**CEFR map (approximate, for dashboards/syllabus/checkpoints):** hsk1 ≈ A1 · hsk2 ≈ A2 ·
hsk3 ≈ B1 · hsk4 ≈ B2 (the "business fluent" gate, with BCT(B) coverage) · hsk5+ ≈ C1.
Real exams exist: HSK (levels sit-able as external proof) and BCT for business register —
name the matching exam level in syllabus.md and checkpoint mocks.

## Unit 0 — bootstrap (lessons 1–4, before the regular recipe)

First-ever run starts here (skip only if the operator asks for a placement test instead):
1. **L1 Pinyin system + tones I**: initials/finals map, the 4 tones + neutral, tone marks;
   production task = record all 4 tones on `ma`; cards = tone-mark recognition.
2. **L2 Tones II — tone pairs**: the 20 tone-pair combinations, anchored with real words wherever
   the known-words list provides a compliant anchor, bare drill syllables (mā-má etc.) for the
   rest — never not-yet-taught vocabulary; introduce third-tone sandhi explicitly.
3. **L3 Characters I**: strokes, stroke order, the 10 most productive radicals from HSK-1
   characters; card type = component breakdown (see below).
4. **L4 First dialogue**: greetings + self-introduction (business register: name, company, role)
   using only words taught in L1–L3 + ≤8 new.
Regular CORE.md recipe starts at L5. Unit 0 lessons use the recipe minus the revenge round,
minus the grammar point (the HSK grammar sequence is untouched until L5), and minus the story
(the serialized story premieres at L5, introduced with its cast in the L4 "coming up" line);
the Corrections section applies from L2 onward as normal. The shadowing script uses the day's
phrases/drills when there is no dialogue yet, and the anticipation drill starts at L2 (graduated
recall tiers that don't exist yet are skipped per CORE). Bare drill syllables (mā/má/mǎ/mà)
are phonology, not vocabulary — exempt from the corpus-only rule per CORE principle 5.

## Tones and characters are first-class (the Duolingo-Chinese failure to avoid)

- **Every** new word is presented with tone marks AND tone numbers on first appearance
  (工作 gōngzuò / gong1zuo4); neutral tone is written as `5` in tone numbers (妈妈 ma1ma5);
  tone-pair pattern named for 2-syllable words.
- Each lesson's revenge round includes 1 tone-pair drill line until `romanization_stage` = `none`.
- Each new character's first appearance gets a one-line component note
  (你 = 亻"person" + 尔; phonetic/semantic role when clean).
- Mandatory sandhi coverage: third-tone sandhi (L2), 不 bù→bú (by L6), 一 yī tone changes (by L8).
- Card types added to CORE rules: tone cards (`拼音 for 工作::gōngzuò (1-4)`) while stage ≠ `none`;
  component cloze for hard characters.

## Romanization staging (pinyin)

- `full` (lessons 1–24): pinyin under every sentence line. Exception: the shadow/drill block stays
  target-script-only in its parseable lines (TTS reads it); those sentences carry pinyin where they
  appear elsewhere in the note.
- `new-only` (lessons 25+, if last checkpoint ≥ 80%): pinyin only on new words and in vocab tables;
  dialogues in characters with pinyin in a collapsed callout.
- `none` (when hsk3 track reached): pinyin in vocab tables only. Never regress the stage.

## Script policy

Simplified is primary everywhere. Traditional shown once in the vocab table (`t` field) when it
differs — recognition only, never tested.

## Business register (operator decision 6C)

- Units 1–2: general business-adjacent survival — greetings/titles, numbers, dates & scheduling,
  phone/WeChat basics, ordering & paying, directions/travel.
- Unit 3+: transactional business — meetings, appointments, email/message frames, small talk with
  counterparts (BCT(A) topic territory).
- From ~2026-11 (month 3), set `profile.business_domain = "guidant-ops"`: scenarios shift toward
  the operator's field — AI/automation consulting, client operations, proposals, project updates —
  still vocabulary-constrained; domain terms beyond the lists are introduced as glossed proper
  nouns/loanwords (人工智能 counts once HSK-listed; "Guidant" stays Latin script).
- Cultural-savvy thread: each unit includes one etiquette note woven into the dialogue
  (business card exchange, 客气 politeness rituals, hierarchy in address, banquet basics, WeChat
  etiquette, gift taboos) — one paragraph, practical, no orientalist trivia.

## Mandarin LLM failure modes → conservative rules

1. Pinyin/tone errors: every pinyin string for a taught word must come from the corpus `p` field —
   copy, never reconstruct. Sandhi noted in prose, not by altering the canonical pinyin.
2. Unnatural textbook Chinese: dialogues favor short, natural utterances; when in doubt use
   patterns from the official grammar list over literary constructions.
3. Word segmentation: vocab tables segment exactly as the corpus does (corpus entry = one unit).
4. Free-generated "common phrases": forbidden — corpus-only (CORE principle 5).

## Story, stages, and the arc (CORE principles 8–9 applied to Mandarin)

- **Story ramp**: episodes 150–300 characters while on hsk1–2 track; 300–500 on hsk3; 500–800 from
  hsk4. Business-world setting (an office, its people, its deals) so register practice is free.
  Simplified characters; pinyin per current `romanization_stage`.
- **External assignments begin** when the hsk3 track starts (≈A2): weekly italki/exchange session,
  one Mandarin Companion-tier graded reader per month, monthly human tone check (Speechling free
  tier — 10 corrections/month — or a tutor session). The tone check is non-optional in spirit:
  tone errors are inaudible to the person making them; this skill structurally cannot hear you.
- **B1 boundary / demotion**: reaching the hsk4 track triggers the CORE principle-9 dashboard
  notice — lessons become the review spine; main input shifts to native media + mining (`mine`
  mode), TCB-style graded news, and regular corrected speaking. Staying courseware-only past hsk4
  is the documented plateau path.

## Invocation

- `/mandarin-coach` or `/mandarin-coach 30` → 30-minute lesson (or checkpoint if lesson % 10 == 0).
- `/mandarin-coach 15` → 15-minute review session.
- `/mandarin-coach friday` → write/extend this week's note in `weekly/` per CORE.md.
- `/mandarin-coach mine <sentence>` → wild-caught sentence intake per CORE.md mine mode
  (segmentation/pinyin verified against corpus; interactive only).
- Headless cron (operator sets up Hermes): same args; CORE.md headless rules apply — idempotent,
  no questions, fail loudly rather than improvise.
