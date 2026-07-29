# Humanizer eval

Use this after the final rewrite. Answer each check with pass or fail. If any check fails, fix the draft before returning it. Run the checks yourself; no separate evaluator agent.

For detect requests, make sure the response names each pattern found with a quoted line and a short fix, without rewriting the draft.

## Fidelity

1. Does the rewrite preserve every claim from the source without adding facts, names, numbers, dates, quotes, or citations?
2. Does it preserve the writer's distinctive vocabulary, cadence, bluntness, humor, uncertainty, digressions, and level of polish (or the provided writing sample's habits)?
3. Does it leave strong human sentences alone instead of rewriting them for consistency?
4. Is the amount of cutting proportional to the actual slop, with no aggressive compression that strips out character?

## Patterns

1. Are content patterns gone: importance puffery, notability padding, superficial -ing analysis, promotional language, weasel attribution, formulaic "challenges" sections?
2. Are language patterns gone: AI vocabulary and banned words (unless quoted as examples), copula avoidance, negative parallelisms, rule of three, synonym cycling, false ranges, subjectless fragments?
3. Are style patterns gone: em/en dashes (unless the writing sample uses them), mechanical boldface, inline-header lists, title-case headings, emojis, curly quotes?
4. Are communication patterns gone: chat artifacts, cutoff disclaimers, speculative gap-fill, sycophancy?
5. Are filler patterns gone: filler phrases, excessive hedging, generic positive conclusions, authority tropes, signposting, fragmented headers, staccato drama, aphorism formulas, fake-candid openers?
6. Are the merged patterns gone: colon reveals, faux-insight setups, fake-profound kickers (deleted, not rewritten into better metaphors), bullets and headers that should be prose?
7. Do summary-recap endings end instead on the last concrete point, takeaway, or next action?

## Final read

1. Does the draft vary sentence length and avoid robotic symmetry, repeated sentence shapes, and stacked punchy fragments?
2. Does it read naturally aloud, and would it sound natural read to a sharp colleague?
3. Would the writer recognize the edited draft as their own voice?
4. Does the output match the invocation mode (draft + bullets + final + What changed for pasted text; file rewritten in place with a short summary for file mode; final text only for embedded; findings only for detect)?
