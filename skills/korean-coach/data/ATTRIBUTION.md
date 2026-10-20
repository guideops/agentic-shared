# Data sources & licenses

- **Word list, grades, frequency ranks, hanja origins** — NIKL 한국어 학습용 어휘 목록 (Korean
  Learner's Vocabulary, 5,965 lemmas in grades A/B/C), National Institute of Korean Language,
  korean.go.kr. License **KOGL Type 1** (attribution only; modification and commercial use
  permitted).
- **RR romanization, IPA, standard pronunciations (sound-change forms), glosses** — English
  Wiktionary Korean extract via [kaikki.org](https://kaikki.org/dictionary/Korean/)
  (CC BY-SA 3.0 / GFDL). Files under `words/` are therefore **CC BY-SA**. ~8% of NIKL lemmas had
  no usable Wiktionary match and are omitted; homographs disambiguated by hanja where NIKL
  provides it.
- **`grammar/particles-endings.json` and `grammar/sequence.md`** — curated for this skill
  (closed-class morphemes and pedagogical ordering; cross-checked against standard Korean L2
  pedagogy — KSI/TOPIK conventions). Editable syllabus, not corpus ground truth.

Format of `words/level{A,B,C}.json`: `{"w": hangul lemma, "rr": Revised Romanization (verbatim
from Wiktionary), "ipa": Seoul-standard IPA, "pron": standard pronunciation in hangul when it
differs from spelling (sound changes, vowel length), "pos": POS, "hanja": hanja origin ("" if
native), "en": up to 3 pipe-joined senses, "rank": NIKL frequency rank, "grade": A|B|C}`.
