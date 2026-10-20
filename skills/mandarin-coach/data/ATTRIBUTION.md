# Data sources & licenses

- **HSK 3.0 (2025 revision) word lists, pinyin, POS, definitions** — processed from [krmanik/HSK-3.0](https://github.com/krmanik/HSK-3.0) (CC BY-SA 4.0). Definitions derive from CC-CEDICT (CC BY-SA 4.0). Word/level data originates from the PRC MoE 《国际中文教育中文水平等级标准》GF0025-2021.
- **HSK grammar point lists per level** — same repo, from the official HSK 3.0 syllabus.
- **BCT (Business Chinese Test) vocabularies** — BCT(A) 600 words, BCT(B) 4000 words, via the same repo; license unstated upstream — used as personal reference only, do not redistribute.
- Files under `words/` and `grammar/` are shared under **CC BY-SA 4.0** accordingly.

Format of `words/hsk*.json`: `{"w": simplified, "t": traditional (empty if same), "p": pinyin, "pos": part of speech, "en": gloss}`.
`bct/*.tsv`: `rank<TAB>word`.
