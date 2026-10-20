# language-coach-core — shared lesson engine

Reference document for the per-language coach skills (`mandarin-coach`, later `korean-coach`, `thai-coach`).
This file is NOT an invocable skill. Each language skill's SKILL.md says "follow CORE.md, then apply
the language-specific rules below." Fix pedagogy here once; it applies to every language.

Design is evidence-grounded (research session 2026-08-05): FSI hour requirements, distributed-practice
literature, WaniKani/Anki longevity patterns, Duolingo learning-science + its documented proficiency
ceiling, and LLM failure modes for tonal/low-resource languages.

## Non-negotiable principles

1. **Production every session.** Recognition-only drilling is the documented "1000-day streak, can't
   talk" failure. A lesson is not complete without free-production tasks and a speaking prompt.
2. **Capped intake, gated progression.** Max **8 new vocabulary items** and **1 new grammar point**
   per lesson. A unit advances only when its checkpoint self-test scores ≥ 80%. Sustainable pace
   beats binge pace — bingers churn.
3. **Difficulty is governed by the known-words list, never by a level label.** Lessons may use ONLY
   words in `state/known-words.json` plus today's new items (proper nouns allowed if glossed inline).
   CEFR-label prompting drifts harder over time; an explicit allowlist is checkable.
4. **Backlog forgiveness.** If the gap since the last lesson is ≥ 7 days, generate a consolidation
   lesson: zero new items, review + production only, no guilt language. Never punish absence.
5. **Corpus-constrained vocabulary.** New words come only from the skill's bundled data files
   (frequency/exam lists), in level order. Never invent "common phrases." Exception: bare-syllable
   phonology/script drills a language skill explicitly mandates (tone drills, alphabet practice)
   are not vocabulary and are exempt.
6. **Anti-repetition.** Read `state/session-log.md` before generating; never re-teach a covered
   topic unless the mistake queue or checkpoint score demands it.
7. **No XP, no leagues, no gamified currency.** Streak calendar and freshness indicators only.
8. **i+1 everywhere.** Any generated sentence — dialogue, story, drill, card — contains at most ONE
   element outside the known-words list (today's new word or the day's grammar pattern). A sentence
   with two unknowns is a bug.
9. **The skill demotes itself.** Generated material is legitimately the main driver from zero to
   ~A2, the spine to ~B1, and a plateau trap beyond it. When the language's B1 boundary is reached
   (defined per language skill), the dashboard must say so and shift the skill's role to: SRS engine
   of record, corrections, domain drills, weekly discipline — while assigning external work (tutor
   sessions, native media, real reading). Learners who stay on courseware past this point plateau;
   a premium system names that instead of hiding it.

## Vault layout (per language)

```
<vault>/Agentic Output/languages/<lang>/
├── dashboard.md            # streak calendar, unit progress, counters, freshness, next milestone
├── lessons/                # YYYY-MM-DD <lang> L<nn> - <topic>.md
├── weekly/                 # YYYY-[W]ww review.md (Friday synthesis + self-test)
├── reference/              # living orientation sheets (see reference-sheet rules)
│   ├── alphabet-chart.md   #   full script/sound-system chart, ✅ per taught element
│   ├── syllabus.md         #   whole roadmap: units → CEFR band → can-dos → vocab targets
│   └── vocab-checklist.md  #   current level's corpus words, ☑ auto-ticked from known-words
├── mining.md               # wild-caught sentence cards (see mine mode) — has #flashcards tag
└── state/
    ├── profile.json        # see schema
    ├── known-words.json    # the difficulty governor
    ├── story-state.json    # serialized-story continuity (see story rules)
    ├── session-log.md      # one line per session: date, lesson #, topics, new items
    └── mistakes.md         # replay queue (see below)
```

Vault root: `$CLAUDE_VAULT` if set, else `/opt/agentic/obsidian/vault`.

## State schemas

`profile.json`:
```json
{
  "language": "mandarin",
  "started": "YYYY-MM-DD",
  "unit": 0,                           // starting unit is defined by the language skill (0 if it has a bootstrap unit)
  "lesson_count": 0,
  "level_track": "hsk1",
  "romanization_stage": "full",        // full | new-only | none  (staging rules per language)
  "business_domain": "general",        // general now; "guidant-ops" from ~month 3 (operator decision 6C)
  "last_session": "YYYY-MM-DD",
  "last_checkpoint_score": null,
  "streak_weeks": 0
}
```
Language skills may add fields (e.g. Thai's `speaker_gender`); unknown fields are preserved,
missing ones backfilled per the schema-migration rule.

`known-words.json`: `{"words": [{"w": "...", "since": "YYYY-MM-DD", "lesson": 3, "fam": 1}], "count": N}`
A word enters when taught; it never leaves (the SR plugin handles forgetting — the list only
constrains generation). `fam` is a LingQ-style familiarity tier 1–4: starts at 1 when taught;
+1 each later week the word reappears in generated content (dialogue/story/drill); set to 4 when
it survives a checkpoint; −1 (min 1) when it lands in the mistake queue. Used for dashboard
counters and for choosing revenge-round/review material (low-fam first) — never to drop a word
from the allowlist.

`story-state.json`: `{"title": "...", "episode": N, "characters": [{"name": "...", "role": "..."}],
"setting": "...", "arc": "one-paragraph where-this-is-going note", "last_summary": "one-line recap
of the previous episode"}` — read before writing each episode, updated after.

`mistakes.md`: markdown list, one item per line:
`- [ ] <item> | <context sentence> | added YYYY-MM-DD | streak 0/2`
The learner (or Friday review) ticks correct recalls; an item clears after 2 consecutive correct.
Skill-side: every Friday self-test miss and every learner-flagged item gets appended.

## Session recipe — 30-minute lesson

Generate ONE note in `lessons/`. Frontmatter: `date, language, lesson, unit, topic, type: lesson,
new_words: [..], grammar: "..."`. Sections, in order:

1. **Today** (1 min read) — heading may pair the target-language word for "today" with "Today" —
   one-line agenda + streak line ("Week 6 · Lesson 14 · Unit 3").
2. **Corrections** (3 min) — read the PREVIOUS lesson note's production block. If the operator wrote
   answers into its answer slots, correct each here: their sentence → corrected version → why, plus
   a naturalness note ("grammatical, but a native would more likely say…") when relevant. If the
   slots are empty, one neutral line ("previous production not submitted — carried to dashboard")
   and mark it on the dashboard. No guilt language, but skips are visible. A previous lesson that
   has no answer slots at all (pre-upgrade notes, 15-min sessions) owes nothing: skip the section
   silently, no dashboard mark.
3. **Revenge round** (4 min) — up to 5 items from `mistakes.md`, oldest first, as active-recall
   prompts (target-language question → answer in a collapsed callout or on the flashcard).
   If the queue is empty, substitute a rapid review of the 5 lowest-`fam` known words; if there
   are also no (or fewer than 5) known words yet, skip or shorten this section with a one-line note.
4. **Core** (10 min) — the ONE new grammar point taught by **guided discovery** (Michel Thomas
   pattern): list the known building blocks; pose 2–3 "How would you say: <English sentence>?"
   challenges with answers in collapsed callouts; THEN the plain-English explanation of the
   derivation (never example-only, never explanation-first). Follow with a dialogue (6–10 exchanges)
   in a business-register scenario using only known words + today's ≤8 new words, every sentence
   obeying i+1 (principle 8). New words listed in a table:
   word | romanization | POS (glossed in English) | meaning | one collocation built from known +
   today's words (omit the cell if nothing natural exists yet).
5. **Story** (4 min) — the next episode of the serialized graded story (see story rules below).
6. **Production block** (6 min) —
   a. 3 English→target free-translation prompts, each followed by an empty answer slot the operator
      fills in (blockquote lines under `**Your answer:**`) — corrected in the NEXT lesson's
      Corrections section. Model answers in `> [!answer]- ` collapsed callouts AFTER the slot;
   b. 1 spoken prompt: "Record yourself answering: <business question>" with a model answer
      collapsed, plus the A/B protocol reminder: play the TTS line, then your recording immediately
      after — contour mismatches you can't hear live are audible in playback;
   c. Shadowing script + **anticipation drill** under `## Shadowing script` (see drill rules) —
      formatted for the operator's agentic-workspace TTS engine. No TTS generation by this skill.
7. **Flashcards** (skim; reviewed daily via plugin) — see card rules.
8. **Coming up** — one line: what next lesson covers, what gates the next unit.

### Story rules (serialized graded reader)
Strongest-evidence upgrade (extensive-reading meta-analyses): volume of reading at ~98% known
vocabulary. One continuing story per language, one episode per 30-min lesson:
- Written STRICTLY from known words + today's new words (i+1 per sentence still applies).
- Length grows with level (language skill sets the ramp; early episodes are very short).
- Continuity from `story-state.json`: recurring characters, business-world setting compatible with
  `business_domain`, each episode ends on a hook; open with the `last_summary` recap line in the
  target language.
- One comprehension question after the episode (answer collapsed); the episode is appended to the
  shadowing script so TTS reading doubles as listening volume.
- Tone: an actual story with stakes and personality, not a disguised drill.
- The unit's etiquette thread plays out in the PLOT (a character misreads hierarchy, hands a
  business card wrong, recovers) — culture lands as narrative consequence, not exposition.

### Anticipation drill rules (Pimsleur pattern)
The shadowing block has two parts:
1. **Shadow**: the dialogue + story episode reprinted clean, target script only, line-per-utterance.
2. **Drill**: forced production under time pressure, as parseable lines:
   ```
   EN: <English cue>
   PAUSE: 3
   TL: <target answer>
   TL: <target answer>        (repeated)
   ```
   8–12 rounds: today's key sentences PLUS graduated recall — 2 sentences from the previous lesson,
   2 from ~2 lessons back, 2 from ~7 lessons back (pull from session-log topics; skip tiers that
   don't exist yet). If the operator's TTS pipeline takes SSML, `PAUSE: 3` maps to
   `<break time="3s"/>`; otherwise it pads silence.

### 15-minute variant
Sections 1, 2, 4 only (revenge round + production), plus flashcards drawn from existing material.
No new words, no new grammar. Used for off-days or when the invocation says `15`.

### Friday weekly review (15 min)
One note in `weekly/`: summary of the week's lessons across ALL active languages this skill family
covers (each language skill writes its own section into the same weekly note if it ran that week);
then per language: 11-item self-test — 5 production, 3 recognition, 2 listening-via-TTS prompts,
**and 1 culture question** drawn from the unit's etiquette thread (a "what do you do when…"
scenario, not trivia) — with answers collapsed, and a `**Score: __/11**` line the operator fills in. Next lesson reads the score:
- ≥ 8 → normal pace; new-word cap stays 8
- 5–7 → cap drops to 5, one consolidation section added
- < 5 → next lesson is consolidation-only; unit does not advance
Misses go to `mistakes.md`. The Friday run is also when `profile.streak_weeks` increments (any week
with ≥ 1 completed session counts).

### Checkpoint (every 10th lesson)
Cumulative 20-item test over the whole unit replaces the Core section, **framed as a level-gate
mock**: open with the unit's CEFR band and its can-do statements (from the language skill's CEFR
map / syllabus.md), and test against them — each can-do gets at least one item. Unit advances only
at ≥ 80%. Record score in `profile.json.last_checkpoint_score` and on the dashboard.

## Flashcard rules (Obsidian Spaced Repetition plugin — settings verified in this vault)

- Deck tag: `#flashcards/<lang>/<unit>` at the top of the flashcard section.
- Single-line: `front::back`. Multiline: front line, `?` on its own line, back lines.
- Cloze: `==hidden==` inside a sentence (highlight-to-cloze is enabled).
- **Production-weighted**: for each new word/pattern, 2 cards minimum —
  one production (English/meaning → target) and one recognition (target → meaning).
  Production direction first; it is the direction apps skip and the reason they plateau.
- **Sentence-pattern cards** (Glossika pattern — sentences, not just words, are SRS items): every
  grammar point gets 3–5 full-sentence production cards (English sentence `::` target sentence),
  drawn from the day's dialogue/story so they carry context. These are in addition to the word
  cards and the 1–2 cloze cards embedding the pattern in a known-words sentence.
- Never edit or renumber old cards in prior notes (the plugin stores scheduling inline as
  HTML comments — rewriting breaks scheduling).

## Dashboard rules

Rewrite `dashboard.md` at the end of every session:
- Streak calendar (per ISO week: ✅ lesson done / ⬜ missed / 🔁 consolidation) — one streak, no
  XP. One cell per week, annotated with which days ran ("✅ Wed L1 + L2") — never render per-day
  ⬜ cells for days before the language started or within the current unfinished week.
- Unit progress bar + lessons completed + **CEFR estimate** ("≈ A1.1", from the language skill's
  CEFR map — always marked approximate) with the current unit's can-do statements one line below.
- **Progress counters** (LingQ pattern — cumulative numbers retain learners for years):
  known words split by familiarity tier (fam 1–4), total story episodes + characters/words read
  (running sum of episode lengths), total production sentences submitted, and **coverage %** of the
  current and next level list ("you know 71% of HSK-2"). All computable from state + session log.
  Coverage counts corpus *entries* (word + reading), not surface strings — a string appearing in
  two levels with different readings counts only for the level whose reading was taught.
- Production accountability line: last 5 lessons' production slots — submitted ✅ / skipped ⬜.
- Freshness badges per past unit: 🟢 reviewed this week · 🟡 1–2 weeks · 🔴 3+ weeks (from
  session-log dates; the badge is a review cue, not a punishment).
- **External assignments** (from the A2-equivalent stage onward, per language skill): a short
  standing list — weekly tutor/exchange session, monthly human tone/pronunciation check, graded
  reading or native-media volume beyond the lessons. At the B1 boundary, add the standing
  demotion notice per principle 9.
- Next milestone in plain words ("Checkpoint at lesson 20 — gates Unit 3").

## Reference sheets (living orientation notes)

Three notes in `reference/`, created on first run and maintained at the end of every session:
- `alphabet-chart.md` — the COMPLETE script/sound-system inventory (all letters/classes/tone
  rules, or the pinyin system for Mandarin) with a status mark per element: ✅ taught (lesson #)
  / ⏳ upcoming (lesson #). The learner sees the whole mountain and how much is climbed.
- `syllabus.md` — the whole roadmap on one page: units → CEFR band (per the language skill's
  map, marked approximate) → 3–5 can-do statements → vocab target counts → exam mapping where a
  real exam exists (HSK/TOPIK). Updated at unit advances; can-dos here are the source the
  checkpoint mock pulls from.
- `vocab-checklist.md` — every corpus word of the CURRENT level as a checkbox line
  (`- [x] word — gloss`), auto-ticked from known-words at session end. Regenerated when the
  level track advances. This makes "A1" a finite, checkable list instead of a fog.

## Mine mode (interactive only)

`/<lang>-coach mine <sentence>` — the Migaku/Refold intake valve for sentences the operator meets
in the wild (a message, a menu, a show). The skill: verifies segmentation and romanization against
the corpus (corpus wins on any conflict; if a word is absent from the corpus, say so and gloss
conservatively from a dictionary-grade reading rather than guessing); identifies the (ideally one)
unknown element; appends to `mining.md` a production card + recognition card with the full sentence
as context; adds genuinely-new corpus words to known-words with `"source": "mined"`, fam 1. Mined
items are eligible for drill rounds. Never available headless.

## Headless / cron behavior

- Never ask questions. Resolve everything from state + data files.
- **One lesson per day maximum**: if ANY lesson note dated today exists for this language
  (regardless of lesson number), exit immediately reporting "already ran today — <note name>",
  without reading further or writing anything. Cron re-fires and manual runs on the same day are
  no-ops, not a license to generate the next lesson early. (Interactive exception: the operator
  explicitly asking for another lesson today overrides this.)
- First run ever (no state dir): create the state files, then generate Lesson 1 as a **placement or
  bootstrap** lesson per the language skill's rules.
- State written under an older schema: backfill missing fields conservatively on read (e.g. missing
  `fam` → 1) and write the current schema back; never fail or reset over a schema gap.
- Date comes from the system clock; write absolute dates everywhere.
- On any corpus-file read error: fail loudly in the note ("generation blocked: <reason>") rather
  than free-generating vocabulary.

## Language-skill responsibilities (what each SKILL.md must define)

1. Corpus file paths + level order (which list feeds `level_track`).
2. Script/phonology bootstrap unit (tones, hangul, Thai script...) before regular lessons.
3. Romanization staging thresholds (when `full` → `new-only` → `none`).
4. Business-register source (BCT topics, KSI Business Korean sequence, ...) and how decision 6C
   (general → operator's domain at ~month 3) applies.
5. Language-specific card types (tone-pair drills, character-component cards, honorific registers).
6. Known LLM failure modes for that language + the conservative rule that neutralizes each.
7. The story length ramp (characters/words per episode by level) and story register.
8. The A2-equivalent stage (external assignments begin) and the B1 boundary (principle-9 demotion),
   in that language's level-track terms.
