---
name: hooks
description: Suggests hooks for a short or long video. Give it one idea, a list of ideas or a script, and it writes 3 hooks in 3 different hook shapes (contrarian, investigator, teacher, experimenter, fortune teller, magician, curiosity gap, versus, list, plus any shapes you add), each short enough to say out loud in the first 3 seconds, with one line on why that shape fits. Writes in your voice when you have a /tone skill and never makes up a fact. Also saves hooks you bookmark into its library, so it learns the patterns you like. Use when the user says "/hooks", "hooks for", "give me hooks", "write a hook", "what hook should I use", "hook ideas", "open my video", "add this hook", "save this hook", or when another skill (like /rubricscripts) asks for hook shapes or hook options.
---

# Hooks

A hook is the first thing people hear or see. Its one job is to make the right person know why they should care, right now. On a short, that is the first 3 seconds. On a long video it is the title, the thumbnail and the first 15 to 30 seconds. This skill writes the spoken opening line; the user's taste picks the winner.

<!-- YOUR DEFAULTS: change these values here, in one place. -->
- Hooks per idea: 3, each in a different shape
- Length: about 3 seconds out loud, roughly 8 to 12 words (one short second sentence is fine)
- Voice skill: /tone
- Shapes and examples: `references/shapes.md` (yours to grow)
<!-- END YOUR DEFAULTS -->

## Rules

1. **Never invent a fact.** [The user says the hook on camera, so a made-up number or result costs them trust.] Every claim comes from the idea, the user's script, a source they gave or a page you opened. If a shape needs a fact you don't have (a result, a number, "I tried it"), ask for it, write a `[fill in]` gap, or pick another shape. Put any line that is only true once the user has done something under "Check before you record".
2. **Three different shapes.** [Three versions of one shape is one choice, not three.] Pick the shapes that fit this idea best, not the same three every time.
3. **Written to be said.** [People decide in about 3 seconds.] Read each hook at talking speed. Cut any word you would trip on. Say the payoff early.
4. **The hook is a promise the video keeps.** [A hook the video doesn't pay off loses the viewer and their trust.] A teacher hook means the viewer learns it by the end. A list on a short stays at about 9 items or fewer, and small numbers beat big ones, so the video feels short enough to finish.
5. **Their voice, not yours.** [The user sounds like themselves on camera.] If the user has a /tone skill, read it first and write every hook through it. If they don't, write plainly and say "No /tone skill found, so these are in a plain voice" at the top.
6. **No long dash character.** Use " - " or a comma, because the long dash reads as written by AI.

## Workflow A: suggest hooks

1. **Get the idea.** One idea, a list (handle each one in turn) or a script (use its main promise). If it's not clear who the video is for, ask once. Done when you can say the idea and its audience in one line each.
2. **Read the shapes.** Open `references/shapes.md`: every shape, its "fits when" and "watch out" lines, and any shapes and examples the user added. Done when you can name every shape in the file.
3. **Check the facts.** List what the idea actually gives you: the claim, the number, the result, the proof. Done when you know which shapes you can write without guessing (rule 1).
4. **Pick 3 shapes.** Match the idea to the "fits when" lines. Breaking news suits the investigator, a result you got suits the experimenter, a countable payoff suits the list, something worth seeing suits the magician. When nothing stands out, the curiosity gap is a safe fallback. Blending two shapes in one line is fine; name both. Done when you have 3 different shapes, best first.
5. **Write and check.** One hook per shape, through /tone if they have it. Read each one out loud in your head and trim to the length in YOUR DEFAULTS. Done when every hook passes rules 1, 3 and 4.
6. **Report** in the format below, then stop. The user picks.

```text
[No /tone skill found, so these are in a plain voice.]   <- only when there is none

1. <Shape>: "<the hook, as said>"
   Why: <one line on why this shape fits this idea>
2. <Shape>: "<hook>"
   Why: <one line>
3. <Shape>: "<hook>"
   Why: <one line>

First frame: <one line on what the screen shows in the first second>
Check before you record: <any line that needs a fact or action from the user, or "nothing">
```

For a list of ideas, repeat the block per idea under the idea as a heading. For a long video, write the same opening line, and note that the title and thumbnail are a separate job. When another skill asks (like /rubricscripts), give it the same three, each as the shape name plus the hook text, so it can file them.

## Workflow B: add a hook or a shape

Runs when the user says "add this hook", "save this hook" or pastes a hook they bookmarked.

1. **Get the hook.** The words as said (or as shown on screen), the creator and the link. Never reword a real hook, and never save one without the user's words or the link. Done when you hold all three, or the user says to skip the link.
2. **Place it.** Find the shape it fits in `references/shapes.md` and add it under that shape's examples, same format as the others. If no shape fits, add a new shape under "Your shapes": its name, a one-liner, "fits when", "watch out" and this hook as its first example. Done when the file is saved.
3. **Report** the shape you filed it under, and the new shape's one-liner if you made one.

## Resources

- [references/shapes.md](references/shapes.md) - the 9 shapes and the visual hook, each with a one-liner, when it fits, what to watch out for and 2 real examples with links, plus the user's own shapes. Read it in Workflow A step 2 and Workflow B step 2.
