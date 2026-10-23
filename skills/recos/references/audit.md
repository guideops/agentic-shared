# The audit

Five areas, in this order. For each one: where to look, and the signs that make a good reco. Use what you already know first, and open a file only to confirm a sign or get its numbers. Every place below is a "where it usually is": setups differ, so look where this user's setup keeps it.

A good reco has three parts you can name: what you saw, what changes, and what the user gains. If you can't name all three, leave it out.

A pillar with no evidence gets 0 recos, and a short list is fine when that is all the evidence supports. An empty pillar is a true result; a padded one wastes the user's time.

## Contents

- Memory (M)
- Skills (S)
- Apps (A)
- Routines (R)
- Workflows you repeat (filed under S)
- Weak recos to leave out

## Memory (M)

**Where:** the instruction files that load at the start of every session (the main rules file in the workspace root, and any it pulls in), your memory or notes folder and its index, and logs of past sessions if you keep them.

**Signs:**

- **A correction that keeps coming back.** The user told you the same thing two or more times. If a rule for it already exists, another rule won't help: the reco is a check that runs on its own (a hook, if your agent supports hooks, or a step in the skill that owns the job).
- **An always-loaded file that is too long.** Instructions that load every session cost tokens every session. Detail that only one job needs belongs in that job's skill. Reco with `saves`.
- **The same fact in two places.** Two copies drift apart and one goes stale. Keep one, link to it from the other.
- **Stale or wrong memory.** A memory that names a file that moved, a plan that changed, or a price that is old.
- **An index that points at nothing.** Memory entries whose files are gone, or files no index points at.

## Skills (S)

**Where:** your skills folder and any commands folder.

**Signs:**

- **Two skills for one job.** Overlapping skills split the know-how, and the wrong one gets picked. Reco: merge them.
- **A skill that is too long.** A main skill file over about 500 lines loads in full every time it runs. Move examples and rare branches into reference files that load only when a step needs them. Reco with `saves`.
- **A description that never fires.** A skill the user has to name by hand, or one that fires on the wrong asks, has a vague description. Reco: rewrite it with the words the user really types.
- **A skill nobody runs.** Not used in months. Reco: archive it, so it stops competing with the skills that matter.
- **A skill that keeps getting corrected.** The same fix after most runs means the skill is missing a rule or a check.

## Apps (A)

**Where:** the tools your agent is connected to (servers, connectors, plugins, extensions), the local apps and servers the user runs (a process manager, open ports), and the apps they open every day.

**Signs:**

- **A connected tool that is never used.** Many agents load every connected tool's description into each session. An unused one costs tokens and adds wrong choices. Reco with `saves`: disconnect it.
- **An app that crashes or restarts a lot.** Check the process manager's restart counts or the app's log.
- **Two apps that do one job.** Pick one.
- **An app with a manual chore.** The user opens it and does the same clicks each time. Reco: let the agent do the clicks, or add the missing button.

## Routines (R)

**Where:** scheduled tasks or routines in your agent, the computer's scheduler (Task Scheduler, cron, launchd), and their run logs.

**Signs:**

- **A routine that fails.** Two or more failed runs in a row. Name the error.
- **A routine on a bigger model than the job needs.** A simple fetch-and-format job on the most expensive model. Reco with `saves`.
- **A routine whose output nobody reads.** It runs, writes a file, and the file is never opened. Reco: stop it, or send the result somewhere the user looks.
- **Work done by hand on a schedule.** The user asks for the same thing every Monday, or every month. Reco: make it a routine. When the user says a job recurs ("I do this every month"), that counts as evidence even if your logs show it only twice.

## Workflows you repeat (filed under S)

**Where:** past sessions and logs, and what you remember of the user's recent asks.

**Sign:** the same multi-step ask three or more times, with no skill that covers it. A job the user says recurs counts too, even if the log shows it only twice. Each time, the user explains the steps again or fixes the same miss. Reco: "Make a skill for X", with the steps you saw as the evidence. These are often the biggest wins on the page, because each one saves the user's time on every run after.

## Weak recos to leave out

- A tip that would fit anyone's setup ("write better prompts", "add more memory").
- A reco with no evidence from this setup.
- A change the user already made, or one they skipped (keep the skipped id so it stays hidden).
- Two recos for the same change. Merge them.
- Anything that needs a key or password in the reco text.
