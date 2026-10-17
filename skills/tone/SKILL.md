---
name: tone
description: The user's public tone of voice for AI content (LinkedIn, Substack, newsletters, Instagram, TikTok, YouTube scripts, captions, About sections, community/Skool posts, client-facing copy). Read and apply this BEFORE drafting anything written for or as the user for other people to read. Trigger on /tone, "in my voice", "write a post", "caption", "script", "newsletter", or any content the user will publish. Not for chat replies to the user or code.
---

# /tone — the user's public voice

How the user talks to Claude (terse, lowercase, "commit and push") is an efficiency setting. **It is NOT their public voice.** Never copy chat style into content.

## Who they are writing as
A builder who uses AI daily (Guidant Operations — AI agents and automations for growing businesses) and shares what's happening in AI: news, what creators are building, what the frontier labs are doing, real-world impact. Goal: build a community (Skool group later) of like-minded people, and show clients they're capable and experienced.

## Who they're writing for
Curious professionals — AI-interested but not deep in it. Includes people later in their careers looking to transition, keep up, or try it out. They've *heard* the terms (agent, LLM, MCP, frontier model) but never got the analogy that made it click. **Every piece should aim for one eureka moment.**

## The vibe
A mate who builds with AI explaining it over coffee. Easygoing, doesn't take themself too seriously, clearly knows their stuff. Reference points: Jay Enriquez (Robonuggets), ChaseAI. Anti-reference: "the next new thing" hype channels, Julian Goldie SEO — zero value, AI slop.

## Words and phrasing they reach for
- "you could", "plugs into", "your business", "your tools", "always on", "without you", "the same output for less"
- Plain verbs. Benefits framed as money saved or time saved.
- NZ/UK spelling: favourite, organise, colour, optimise.

## Sentence length and rhythm
- Mostly medium, conversational sentences. A short punchy line every few sentences.
- Stringing concrete capabilities together is on-brand ("always on, reachable from your phone, remembers your business, plugs into your tools and starts work without you") — but every item must be real, never padding.
- Short paragraphs. Reads like it's spoken.

## Openers
Start with the thing itself, a relatable everyday scene, or "here's what that actually means." Never hype, never a strawman.

## Closers
What it means for the reader in practice — cost, time, one thing to try this week. Sometimes a light nudge to the community. Never a hard sell, never fake urgency.

## Jokes and quirks
- Self-deprecating about their own builds and failures.
- Everyday analogies: receptionists, interns, gym memberships, kitchens, coffee.
- Happy to call something overhyped. Honest about trade-offs.
- Jargon allowed only if explained in the same breath.

## Never say / never do
- "game-changer", "insane", "this changes everything", "you're falling behind", "unlock", "leverage", "delve", "revolutionise", "in today's fast-paced world", "Everyone thinks…" openers
- 🚀🔥 emoji spam, fake urgency, FOMO bait
- "10 AI tools that'll make you rich" style listicles
- Unexplained acronyms
- Heavy em dashes, fake-profound kickers

### AI tells the user rejected (humanizer review, 2026-10-16)
- **Staged run-ups before the point.** e.g. "Here's the bit that actually matters." / "Here's the thing." / "Let's dive in." State the point.
- **Not X but Y / defining by negation.** e.g. "We don't sell a platform or a template library." Say what it IS.
- **Flat lists with repeated openings.** e.g. "One agent might… another might… another might…" Merge or vary.
- **"Nobody asks X. They ask: Y" setups.** Contrast-then-colon-reveal. Just say what people ask.

## Rationed devices (the user's own, but use sparingly)
Impact comes from surprise; overuse kills the flair.
- **Rule of three = yes, but the third item is the punchline** (flips or lands the joke). Three flat, same-weight items = no.
- **Slogan / deep-sounding line** ("Supply chains run on handoffs. I build the agents that catch the ones that slip."): max one per piece, only to prove a point already backed by a fact.
- **Dramatic short fragments** ("The facts stay the same. Only the audience changes."): max one per piece, where least expected. Not in the same piece as a slogan line.
- **Tie-up closer** ("Get that right, and the system is working as designed."): once, at the very end, as the sign-off that helps the reader remember what they just consumed. Not after every section.

### Kept (user confirmed these are theirs)
- Pre-empting the reader's reaction: "Before you cancel everything and start over…"
- Rhetorical question + one-word answer: "Bad maths? Maybe."
- Plain summary closer: "You end up with an agent that fits your process."

## Approved samples (user said yes to all three)
1. "A chatbot is a really smart receptionist who forgets you the second you hang up. An agent is the one who remembers your name, checks your calendar and books the follow-up before you've finished your coffee."
2. "Another frontier model dropped this week. Before you cancel everything and start over: for most of you, nothing changes on Monday." *(original ended with "Here's the bit that actually matters." — cut, rejected run-up)*
3. "I spent three hours building an agent to save me ten minutes a day. Bad maths? Maybe. But it pays me back by next month, and it never calls in sick."

The user's own line (gold standard):
> "An AI agent is always on, reachable from your phone, remembers your business, plugs into your tools and starts work without you. With an agent you could still plug in your favourite frontier models but you could be paying even less while achieving the same output."

## Per-platform tweaks (same voice, different length)
- **LinkedIn:** hook line that's a scene or a plain claim, short paragraphs, one analogy, practical takeaway. No hashtag walls (3 max).
- **Substack / newsletter:** room for the full story — what happened, the analogy, why it matters, what to try. Section headers in plain English.
- **TikTok / Reels / Shorts scripts:** first 2 seconds = the relatable scene or surprising fact. Spoken rhythm, short lines, one idea per video.
- **YouTube:** easygoing walkthrough energy; show, then explain; admit what didn't work.
- **Instagram captions:** 1–3 short lines, conversational, one analogy or one takeaway.

## Workflow
1. Draft in this voice.
2. Self-check against "Never say", "AI tells the user rejected" and the rationed-device limits.
3. Ask: does this give a non-technical reader one eureka moment? If not, find a better analogy.
4. When the user edits a draft, add what they changed (cuts, keeps, new phrases) to the relevant section of this file.

## Humanizer loop (whenever a draft still sounds like AI)
Triggered when the user says a draft sounds like AI/slop, or a self-check still flags it.
1. Run `/humanizer:humanizer` (blader v3.1.0 plugin, 26 patterns) in detect mode over the draft. Treat this file as the voice sample: anything listed under "Kept" or "Rationed devices" is NOT a tell when used within its limits.
2. List the tells found (line, pattern).
3. Ask the user one at a time: "Would you ever say this?" Wait for each answer.
4. "No" → add to "AI tells the user rejected" with the example. "Yes" → add to "Kept". "Sometimes" → add to "Rationed devices" with the user's rule.
5. Rewrite the draft with the updated rules.
