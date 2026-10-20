# Data sources & licenses

- **Word frequency ranking** — Thai National Corpus frequency list via
  [PyThaiNLP](https://github.com/PyThaiNLP/pythainlp) (`tnc_freq.txt`); PyThaiNLP corpus data
  released CC0/permissive.
- **Romanization (Paiboon + RTGS), IPA, POS, glosses** — English Wiktionary Thai extract via
  [kaikki.org](https://kaikki.org/dictionary/Thai/) (CC BY-SA 3.0 / GFDL). Files under `words/`
  are therefore **CC BY-SA**.
- **`grammar/sequence.md`** — curated for this skill (not an official standard; Thai has no
  public L2 level lists). Sequencing cross-checked against standard Thai pedagogy (FSI Thai
  Basic Course structure, Smyth's *Thai: An Essential Grammar* topic order). Treat as editable
  syllabus, not corpus ground truth.

Format of `words/tier*.json`: `{"w": Thai, "pb": Paiboon romanization (tone-marked — the taught
system), "rtgs": Royal Institute romanization, "ipa": IPA with tone letters, "pos": comma-joined
POS, "en": up to 3 pipe-joined Wiktionary senses, "rank": TNC frequency rank}`.
Tiers: tier1 = top 400 joined words, tier2 = next 600, tier3 = next 1000, tier4 = next 1500.
