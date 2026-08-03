# regional-bugle source packs

One pack per region. The skill reads this file every run and appends new packs
discovered in fallback mode. Keep the format exactly as below so runs can parse it.

- **Status**: `verified` = a human or a run confirmed the feed returns valid RSS/Atom.
  `auto` = added by fallback mode, not yet human-reviewed — skim before trusting.
- **Lang**: feed language. Non-`en` feeds are pulled in the local language and
  translated per the SKILL.md translation rules.
- **Tier**: `wire` (agency/public broadcaster) > `daily` (major newspaper) >
  `indie` (credible independent). Headlines need a wire or daily source.

## new-zealand (default)
| Source | Feed | Lang | Tier | Status |
|---|---|---|---|---|
| RNZ National | https://www.rnz.co.nz/rss/national.xml | en | wire | verified 2026-08-03 |
| NZ Herald | https://rss.nzherald.co.nz/rss/xml/nzhrsscid_000000001.xml | en | daily | verified 2026-08-03 |
| Stuff | https://www.stuff.co.nz/rss | en | daily | verified 2026-08-03 |

## thailand
| Source | Feed | Lang | Tier | Status |
|---|---|---|---|---|
| Bangkok Post — Top | https://www.bangkokpost.com/rss/data/topstories.xml | en | daily | verified 2026-08-03 |
| Bangkok Post — Thailand | https://www.bangkokpost.com/rss/data/thailand.xml | en | daily | verified 2026-08-03 |
| Khaosod English | https://www.khaosodenglish.com/feed/ | en | daily | verified 2026-08-03 |
| Prachatai English | https://prachataienglish.com/rss.xml | en | indie | verified 2026-08-03 |
| Thairath | https://www.thairath.co.th/rss/news | th | daily | verified 2026-08-03 |

## australia
| Source | Feed | Lang | Tier | Status |
|---|---|---|---|---|
| ABC News | https://www.abc.net.au/news/feed/51120/rss.xml | en | wire | verified 2026-08-03 |
| Guardian Australia | https://www.theguardian.com/australia-news/rss | en | daily | verified 2026-08-03 |
| SBS News | https://www.sbs.com.au/news/feed | en | wire | verified 2026-08-03 |
| Sydney Morning Herald | https://www.smh.com.au/rss/feed.xml | en | daily | verified 2026-08-03 |

## united-kingdom
| Source | Feed | Lang | Tier | Status |
|---|---|---|---|---|
| BBC UK | https://feeds.bbci.co.uk/news/uk/rss.xml | en | wire | verified 2026-08-03 |
| Guardian UK | https://www.theguardian.com/uk-news/rss | en | daily | verified 2026-08-03 |
| Sky News UK | https://feeds.skynews.com/feeds/rss/uk.xml | en | wire | verified 2026-08-03 |

## south-korea
| Source | Feed | Lang | Tier | Status |
|---|---|---|---|---|
| Yonhap (English) | https://en.yna.co.kr/RSS/news.xml | en | wire | verified 2026-08-03 |
| Korea Herald | https://www.koreaherald.com/rss/kh_main | en | daily | verified 2026-08-03 |
| Hankyoreh (English) | https://english.hani.co.kr/rss/ | en | daily | verified 2026-08-03 |
| Yonhap (Korean) | https://www.yna.co.kr/rss/news.xml | ko | wire | verified 2026-08-03 |

## usa
| Source | Feed | Lang | Tier | Status |
|---|---|---|---|---|
| NPR News | https://feeds.npr.org/1001/rss.xml | en | wire | verified 2026-08-03 |
| PBS NewsHour | https://www.pbs.org/newshour/feeds/rss/headlines | en | wire | verified 2026-08-03 |
| NYT — US | https://rss.nytimes.com/services/xml/rss/nyt/US.xml | en | daily | verified 2026-08-03 |
| Washington Post — National | https://feeds.washingtonpost.com/rss/national | en | daily | verified 2026-08-03 |

## Known-dead (do not re-add without re-testing)
- Thai PBS World `thaipbsworld.com/feed/` and `/rss` — returns HTML, not a feed (2026-08-03)
- Nation Thailand `nationthailand.com/rss` — returns HTML, not a feed (2026-08-03)
- Korea JoongAng Daily `koreajoongangdaily.joins.com/xmls/joins` — 404 (2026-08-03)
