---
name: feedback-to-fix
description: Resolve corrective coding feedback when requirements conflict with existing behavior, a fix keeps failing, or completion lacks relevant evidence. Choose the next action using uncertainty and the consequences of being wrong. Skip exact mechanical edits, general advice, and tasks without a meaningful unresolved decision.
---

# Feedback to Fix

Choose the next useful action before making the next edit. Optimize for the
requested outcome and the effort needed to reach it, including rework.

## Find the unresolved decision

Read the latest request and the relevant existing code or evidence. Distinguish:

- **Requested:** what the user wants to happen, including constraints to preserve.
- **Observed:** what code, a reproduction, or a check actually establishes.
- **Assumed:** an explanation or preference not yet supported by those sources.

Keep these distinctions brief. Do not produce a separate plan, checklist, or
project file for an obvious edit. Use a concise decision note when a real
conflict or tradeoff needs to be visible.

An explicit implementation choice is a constraint. When it appears incompatible
with the requested outcome, explain the conflict and offer a concrete option;
do not silently substitute your own product or goal.

## Choose one next action

| Situation | Next action | What makes it sufficient |
| --- | --- | --- |
| Outcome is clear; the change is local and reversible | Implement using the closest existing pattern | Preserve the connected behavior the request relies on |
| A proposed fix depends on an untested causal explanation | Inspect or run the cheapest check that distinguishes plausible causes | Name what each result would change about the fix |
| Missing information can be found in the repo or current session | Retrieve it | Avoid asking the user to repeat available information |
| An unresolved choice could change data, access, an external commitment, or the user's intended outcome | Ask one focused question | Include what is known and why the answer changes the action |
| A failed attempt contradicts the working explanation | Revise the explanation before another edit | Do not stack a new workaround on an explanation the result undermines |
| A claim has broader scope than its evidence | Verify the missing behavior, or narrow the claim | Report a precise limit when the relevant check is unavailable |
| The requested outcome and connected behavior have sufficient evidence | Finish | Reopen only for new relevant evidence or an unmet requirement |

Use existing authorization. Routine reversible work does not need an additional
approval checkpoint. A task's urgency changes the acceptable investigation cost,
not the meaning of success or the user's constraints.

## Keep the fix complete and bounded

Trace callers, validation, state, and tests only as far as the changed behavior
requires. A shared cause can justify several files; a small file count does not
prove a fix is complete. Adjacent cleanup needs its own justification.

Current user instructions can supersede an old test. Identify the conflict,
update the relevant expectation, and preserve independent regression coverage.
Do not weaken an assertion solely to turn a failure green. Ask only when the
active requirements themselves remain incompatible after reading the context.

When another attempt fails, state the changed observation and what it rules out.
If the observation adds no information, change the diagnostic method instead of
repeating the same edit. Unchanged facts and files do not need another full read.

## Match completion to evidence

Choose checks that can expose the original failure and protect connected
behavior. A successful build establishes compilation, a mocked test establishes
the simulated path, and a browser check establishes the interaction it exercised.
Use the layer needed by the task; do not require every layer for every edit.

Rerun relevant checks after changes that could invalidate them. If a check cannot
run, continue independent work and identify the remaining uncertainty. Describe
the current implementation without claiming an unobserved result.

Finish with the outcome, the relevant evidence, and any material unresolved
limit. Keep the response proportional to the change. Do not invent measurements
or silently expand scope. Create extra artifacts only when requested or required
by the established workflow; keep session history out of deliverables.

For ambiguous cases, consult [decision examples](references/decision-examples.md).
